from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import and_, select

from app.dependencies import CurrentUser, DB
from app.models import Card, StudyProgress, StudySession, StudySet
from app.schemas.session import (
    AnswerResponse,
    AnswerSubmit,
    CardInSession,
    CardStatus,
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