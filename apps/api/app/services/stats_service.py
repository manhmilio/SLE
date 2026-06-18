from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct, case

from app.models.user import User
from app.models.learning import StudyProgress, StudySession
from app.schemas.stats import StatsOverviewResponse

KNOWN_THRESHOLD_DAYS = 7


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