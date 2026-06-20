from datetime import datetime, date, timedelta, timezone
from sqlalchemy import select, func, distinct, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.content import StudySet
from app.models.learning import StudySession
from app.schemas.admin import (
    DashboardResponse,
    UserMetrics,
    SetMetrics,
    SessionMetrics,
    ActiveUserMetrics,
    ChartPoint,
)

VALID_RANGES = {"7d": 7, "30d": 30, "90d": 90}


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _today_utc() -> date:
    return _now_utc().date()


async def get_dashboard(
    db: AsyncSession,
    range_str: str = "7d",
) -> DashboardResponse:
    today = _today_utc()
    now = _now_utc()
    days = VALID_RANGES.get(range_str, 7)
    start_date = today - timedelta(days=days - 1)
    start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)

    # ── User metrics ──────────────────────────────────────────────
    total_users = await db.scalar(select(func.count()).select_from(User))
    active_users_count = await db.scalar(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    )
    inactive_users_count = await db.scalar(
        select(func.count()).select_from(User).where(User.is_active.is_(False))
    )
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    new_today = await db.scalar(
        select(func.count()).select_from(User).where(User.created_at >= today_start)
    )
    week_start = datetime(
        (today - timedelta(days=6)).year,
        (today - timedelta(days=6)).month,
        (today - timedelta(days=6)).day,
        tzinfo=timezone.utc,
    )
    new_7d = await db.scalar(
        select(func.count()).select_from(User).where(User.created_at >= week_start)
    )

    # ── Set metrics ───────────────────────────────────────────────
    total_sets = await db.scalar(select(func.count()).select_from(StudySet))
    public_sets = await db.scalar(
        select(func.count()).select_from(StudySet).where(StudySet.is_public.is_(True))
    )

    # ── Session metrics ───────────────────────────────────────────
    month_start = datetime(
        (today - timedelta(days=29)).year,
        (today - timedelta(days=29)).month,
        (today - timedelta(days=29)).day,
        tzinfo=timezone.utc,
    )
    sessions_today = await db.scalar(
        select(func.count())
        .select_from(StudySession)
        .where(
            and_(
                StudySession.ended_at.is_not(None),
                StudySession.created_at >= today_start,
            )
        )
    )
    sessions_7d = await db.scalar(
        select(func.count())
        .select_from(StudySession)
        .where(
            and_(
                StudySession.ended_at.is_not(None),
                StudySession.created_at >= week_start,
            )
        )
    )
    sessions_30d = await db.scalar(
        select(func.count())
        .select_from(StudySession)
        .where(
            and_(
                StudySession.ended_at.is_not(None),
                StudySession.created_at >= month_start,
            )
        )
    )

    # ── DAU / MAU ─────────────────────────────────────────────────
    dau = await db.scalar(
        select(func.count(distinct(StudySession.user_id)))
        .where(
            and_(
                StudySession.ended_at.is_not(None),
                StudySession.created_at >= today_start,
            )
        )
    )
    mau = await db.scalar(
        select(func.count(distinct(StudySession.user_id)))
        .where(
            and_(
                StudySession.ended_at.is_not(None),
                StudySession.created_at >= month_start,
            )
        )
    )

    # ── User growth chart (users đăng ký theo ngày) ───────────────
    user_day_trunc = func.date_trunc("day", User.created_at)
    user_growth_rows = (
        await db.execute(
            select(
                user_day_trunc.label("day"),
                func.count().label("cnt"),
            )
            .where(User.created_at >= start_dt)
            .group_by(user_day_trunc)
            .order_by(user_day_trunc)
        )
    ).all()
    user_growth_map: dict[str, int] = {
        row.day.date().isoformat(): row.cnt for row in user_growth_rows
    }
    user_growth: list[ChartPoint] = []
    current = start_date
    while current <= today:
        user_growth.append(
            ChartPoint(date=current.isoformat(), count=user_growth_map.get(current.isoformat(), 0))
        )
        current += timedelta(days=1)

    # ── Session chart (sessions theo ngày) ────────────────────────
    session_day_trunc = func.date_trunc("day", StudySession.created_at)
    session_chart_rows = (
        await db.execute(
            select(
                session_day_trunc.label("day"),
                func.count().label("cnt"),
            )
            .where(
                and_(
                    StudySession.ended_at.is_not(None),
                    StudySession.created_at >= start_dt,
                )
            )
            .group_by(session_day_trunc)
            .order_by(session_day_trunc)
        )
    ).all()
    session_chart_map: dict[str, int] = {
        row.day.date().isoformat(): row.cnt for row in session_chart_rows
    }
    session_chart: list[ChartPoint] = []
    current = start_date
    while current <= today:
        session_chart.append(
            ChartPoint(
                date=current.isoformat(),
                count=session_chart_map.get(current.isoformat(), 0),
            )
        )
        current += timedelta(days=1)

    return DashboardResponse(
        users=UserMetrics(
            total=total_users or 0,
            active=active_users_count or 0,
            inactive=inactive_users_count or 0,
            new_today=new_today or 0,
            new_7d=new_7d or 0,
        ),
        sets=SetMetrics(
            total=total_sets or 0,
            public=public_sets or 0,
            private=(total_sets or 0) - (public_sets or 0),
        ),
        sessions=SessionMetrics(
            today=sessions_today or 0,
            last_7d=sessions_7d or 0,
            last_30d=sessions_30d or 0,
        ),
        active_users=ActiveUserMetrics(dau=dau or 0, mau=mau or 0),
        user_growth=user_growth,
        session_chart=session_chart,
    )