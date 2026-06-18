from __future__ import annotations
import uuid
from datetime import datetime, date, timedelta, timezone   # thêm datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, case

from app.models.user import User
from app.models.learning import StudyProgress, StudySession
from app.schemas.stats import (                            # chuyển lên top
    StatsOverviewResponse,
    SessionHistoryItem,
    SessionHistoryResponse,
)

KNOWN_THRESHOLD_DAYS = 7
RANGE_DAYS: dict[str, int] = {"7d": 7, "30d": 30, "90d": 90}


async def get_overview(db: AsyncSession, user_id: uuid.UUID) -> StatsOverviewResponse:
    # 1. Streak + last_studied từ bảng users
    user_result = await db.execute(
        select(User.streak, User.last_studied).where(User.id == user_id)
    )
    user_row = user_result.one()

    # 2. Card counts — dùng max(interval) per card để classify
    #    Một card có thể có nhiều progress records (mỗi mode 1 record)
    #    → known nếu max interval >= 7, learning nếu < 7
    max_interval_subq = (
        select(
            StudyProgress.card_id,
            func.max(StudyProgress.interval).label("max_interval"),
        )
        .where(StudyProgress.user_id == user_id)
        .group_by(StudyProgress.card_id)
        .subquery()
    )

    card_stats_result = await db.execute(
        select(
            func.count(
                case(
                    (max_interval_subq.c.max_interval >= KNOWN_THRESHOLD_DAYS, 1),
                    else_=None,
                )
            ).label("known"),
            func.count(
                case(
                    (max_interval_subq.c.max_interval < KNOWN_THRESHOLD_DAYS, 1),
                    else_=None,
                )
            ).label("learning"),
        ).select_from(max_interval_subq)
    )
    card_row = card_stats_result.one()

    # 3. Session stats — chỉ tính sessions đã ended
    session_stats_result = await db.execute(
        select(
            func.count(StudySession.id).label("total_sessions"),
            func.coalesce(
                func.sum(
                    func.extract(
                        "epoch",
                        StudySession.ended_at - StudySession.created_at,
                    )
                ),
                0,
            ).label("total_seconds"),
            func.count(distinct(StudySession.study_set_id)).label("sets_studied"),
        ).where(
            StudySession.user_id == user_id,
            StudySession.ended_at.is_not(None),
        )
    )
    session_row = session_stats_result.one()

    return StatsOverviewResponse(
        streak=user_row.streak,
        last_studied=user_row.last_studied,
        total_cards_known=card_row.known or 0,
        total_cards_learning=card_row.learning or 0,
        total_sessions=session_row.total_sessions or 0,
        total_study_time_seconds=int(session_row.total_seconds or 0),
        sets_studied=session_row.sets_studied or 0,
    )


async def get_sessions_history(
    db: AsyncSession,
    user_id: uuid.UUID,
    time_range: str,
    group_by: str,
) -> "SessionHistoryResponse":

    days = RANGE_DAYS.get(time_range, 7)
    now = datetime.now(timezone.utc)
    start_dt = now - timedelta(days=days)

    # DATE_TRUNC theo day hoặc week
    trunc_unit = "week" if group_by == "week" else "day"
    period_expr = func.date_trunc(trunc_unit, StudySession.ended_at).label("period")

    result = await db.execute(
        select(
            period_expr,
            func.count(StudySession.id).label("sessions"),
            func.coalesce(func.sum(StudySession.cards_studied), 0).label("cards_studied"),
            func.coalesce(func.sum(StudySession.correct), 0).label("correct"),
            func.coalesce(func.sum(StudySession.incorrect), 0).label("incorrect"),
            func.coalesce(
                func.sum(
                    func.extract("epoch", StudySession.ended_at - StudySession.created_at)
                ),
                0,
            ).label("study_time_seconds"),
        )
        .where(
            StudySession.user_id == user_id,
            StudySession.ended_at.is_not(None),
            StudySession.ended_at >= start_dt,
        )
        .group_by(period_expr)
        .order_by(period_expr)
    )
    rows = result.all()

    # Build lookup: date string → row
    db_data: dict[str, object] = {}
    for row in rows:
        key = row.period.date().isoformat()
        db_data[key] = row

    # Helper build item
    def make_item(key: str, row=None) -> SessionHistoryItem:
        if row is None:
            return SessionHistoryItem(
                date=key,
                sessions=0,
                cards_studied=0,
                correct=0,
                incorrect=0,
                accuracy=0.0,
                study_time_seconds=0,
            )
        cards = int(row.cards_studied or 0)
        correct = int(row.correct or 0)
        incorrect = int(row.incorrect or 0)
        accuracy = round(correct / cards * 100, 1) if cards > 0 else 0.0
        return SessionHistoryItem(
            date=key,
            sessions=int(row.sessions),
            cards_studied=cards,
            correct=correct,
            incorrect=incorrect,
            accuracy=accuracy,
            study_time_seconds=int(row.study_time_seconds or 0),
        )

    # Generate full date/week range, fill 0 cho ngày không có data
    data: list[SessionHistoryItem] = []
    current = start_dt.date()
    end_date = now.date()

    if group_by == "week":
        # Lùi về thứ Hai của tuần chứa start_dt
        current = current - timedelta(days=current.weekday())
        while current <= end_date:
            key = current.isoformat()
            data.append(make_item(key, db_data.get(key)))
            current += timedelta(weeks=1)
    else:
        while current <= end_date:
            key = current.isoformat()
            data.append(make_item(key, db_data.get(key)))
            current += timedelta(days=1)

    return SessionHistoryResponse(range=time_range, group_by=group_by, data=data)