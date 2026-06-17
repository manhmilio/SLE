from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import and_, select

from uuid import UUID
from app.dependencies import CurrentUser, DB
from app.models import Card, SessionAnswer, StudyProgress, StudySession, StudySet
from app.schemas.session import (
    AnswerResponse,
    AnswerSubmit,
    CardInSession,
    CardStatus,
    SM2Result,
    SessionCreate,
    SessionCreateResponse,
    SessionEndResponse,
    SessionListItem,
    SessionListResponse,
    StudyMode,
)
from app.services.sm2_service import KNOWN_THRESHOLD_DAYS, SM2Input, calculate_sm2, map_quality

router = APIRouter(prefix="/sessions", tags=["sessions"])


# ── Helper ─────────────────────────────────────────────────────────────────────
def _derive_status(progress) -> CardStatus:
    """StudyProgress không có cột status → derive từ interval."""
    if progress is None:
        return CardStatus.not_started
    if progress.interval >= KNOWN_THRESHOLD_DAYS:
        return CardStatus.known
    return CardStatus.learning


# ── POST /sessions ─────────────────────────────────────────────────────────────
@router.post("", response_model=SessionCreateResponse, status_code=201)
async def create_session(
    body: SessionCreate,
    current_user: CurrentUser,
    db: DB,
):
    # 1. Kiểm tra set tồn tại
    set_row = await db.get(StudySet, body.set_id)
    if not set_row:
        raise HTTPException(status_code=404, detail="Study set not found")

    # 2. Kiểm tra quyền: owner hoặc set public
    if set_row.owner_id != current_user.id and not set_row.is_public:
        raise HTTPException(status_code=403, detail="Access denied")

    # 3. Tạo session mới
    now = datetime.now(timezone.utc)
    session = StudySession(
        user_id=current_user.id,
        study_set_id=body.set_id,
        mode=body.mode.value,
        cards_studied=0,
        correct=0,
        incorrect=0,
    )
    db.add(session)
    await db.flush()  # lấy session.id

    # 4. Lấy cards + SM-2 state (LEFT JOIN study_progress)
    stmt = (
        select(Card, StudyProgress)
        .outerjoin(
            StudyProgress,
            and_(
                StudyProgress.card_id == Card.id,
                StudyProgress.user_id == current_user.id,
                StudyProgress.mode == body.mode.value,
            ),
        )
        .where(Card.study_set_id == body.set_id)
        .order_by(Card.order)
    )
    rows = (await db.execute(stmt)).all()

    # 5. Lọc cards due hôm nay
    due_cards = [
        (card, progress)
        for card, progress in rows
        if progress is None or progress.next_review <= now
    ]

    # Không có card nào due → trả về toàn bộ
    cards_to_study = due_cards if due_cards else rows

    # 6. Build response
    card_responses = [
        CardInSession(
            id=card.id,
            front=card.front,
            back=card.back,
            image_url=card.image_url,
            order=card.order,
            next_review=progress.next_review if progress else None,
            status=_derive_status(progress),
        )
        for card, progress in cards_to_study
    ]

    await db.commit()

    return SessionCreateResponse(
        id=session.id,
        set_id=session.study_set_id,
        mode=StudyMode(session.mode),
        started_at=session.created_at,
        cards=card_responses,
    )


# ── POST /sessions/:id/answers ─────────────────────────────────────────────────
@router.post("/{session_id}/answers", response_model=AnswerResponse)
async def submit_answer(
    session_id: UUID,
    body: AnswerSubmit,
    current_user: CurrentUser,
    db: DB,
):
    # 1. Kiểm tra session tồn tại và thuộc user
    session = await db.get(StudySession, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Kiểm tra session còn mở
    if session.ended_at is not None:
        raise HTTPException(status_code=400, detail="Session already ended")

    # 3. Kiểm tra card thuộc set của session
    card = await db.get(Card, body.card_id)
    if not card or card.study_set_id != session.study_set_id:
        raise HTTPException(status_code=404, detail="Card not found in this session")

    # 4. Map quality theo mode
    try:
        quality = map_quality(body.is_correct, session.mode, body.quality)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 5. Lấy StudyProgress hiện tại (nếu có)
    stmt = select(StudyProgress).where(
        and_(
            StudyProgress.user_id == current_user.id,
            StudyProgress.card_id == body.card_id,
            StudyProgress.mode == session.mode,
        )
    )
    progress = (await db.execute(stmt)).scalar_one_or_none()

    # 6. Tính SM-2
    current_sm2 = SM2Input(
        ease_factor=progress.ease_factor if progress else 2.5,
        interval=progress.interval if progress else 0,
        repetitions=progress.repetitions if progress else 0,
    )
    result = calculate_sm2(current_sm2, quality)

    # 7. Upsert StudyProgress
    now = datetime.now(timezone.utc)
    if progress is None:
        progress = StudyProgress(
            user_id=current_user.id,
            card_id=body.card_id,
            study_set_id=session.study_set_id,
            mode=session.mode,
            ease_factor=result.ease_factor,
            interval=result.interval,
            repetitions=result.repetitions,
            next_review=result.next_review,
            last_reviewed=now,
            streak=result.repetitions,
        )
        db.add(progress)
    else:
        progress.ease_factor = result.ease_factor
        progress.interval = result.interval
        progress.repetitions = result.repetitions
        progress.next_review = result.next_review
        progress.last_reviewed = now
        progress.streak = result.repetitions if body.is_correct else 0

    # 8. Insert SessionAnswer (snapshot nội dung tại thời điểm trả lời)
    answer = SessionAnswer(
        session_id=session_id,
        user_id=current_user.id,
        card_id=body.card_id,
        front=card.front,
        back=card.back,
        user_answer=body.user_answer,
        quality=quality,
        is_correct=body.is_correct,
        time_spent=body.time_spent,
    )
    db.add(answer)

    # 9. Cập nhật counters của session
    session.cards_studied += 1
    if body.is_correct:
        session.correct += 1
    else:
        session.incorrect += 1

    await db.commit()

    return AnswerResponse(
        card_id=body.card_id,
        is_correct=body.is_correct,
        quality=quality,
        sm2=SM2Result(
            ease_factor=result.ease_factor,
            interval=result.interval,
            repetitions=result.repetitions,
            next_review=result.next_review,
            status=CardStatus(result.status),
        ),
    )