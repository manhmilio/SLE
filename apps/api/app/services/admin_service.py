from datetime import datetime, date, timedelta, timezone
from sqlalchemy import select, func, distinct, and_
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
from uuid import UUID
from sqlalchemy import select, func, distinct, and_, or_, update, desc, asc
from fastapi import HTTPException, status as http_status
from app.core.security import hash_password

from app.models.user import User
from app.models.content import StudySet
from app.models.learning import StudySession
from app.models.user import User, RefreshToken
from app.models.content import Card
from app.schemas.admin import (
    DashboardResponse,
    UserMetrics,
    SetMetrics,
    SessionMetrics,
    ActiveUserMetrics,
    ChartPoint,
    AdminUserListItem,
    AdminUserListResponse,
    DeviceInfo,
    RecentSessionItem,
    AdminUserDetailResponse,
    AdminUserUpdateRequest,
    AdminUserUpdateResponse,
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


# ═══════════════════════ User Management ═══════════════════════

def _not_found(resource: str = "User"):
    return HTTPException(
        status_code=http_status.HTTP_404_NOT_FOUND,
        detail={"success": False, "error": {"code": "NOT_FOUND", "message": f"{resource} not found"}},
    )


def _bad_request(message: str):
    return HTTPException(
        status_code=http_status.HTTP_400_BAD_REQUEST,
        detail={"success": False, "error": {"code": "BAD_REQUEST", "message": message}},
    )


async def get_users_list(
    db: AsyncSession,
    search: str | None,
    role: str | None,
    is_active: bool | None,
    sort_by: str,
    sort_order: str,
    page: int,
    limit: int,
) -> AdminUserListResponse:
    sets_count_subq = (
        select(StudySet.owner_id, func.count(StudySet.id).label("total_sets"))
        .group_by(StudySet.owner_id)
        .subquery()
    )
    sessions_count_subq = (
        select(StudySession.user_id, func.count(StudySession.id).label("total_sessions"))
        .where(StudySession.ended_at.is_not(None))
        .group_by(StudySession.user_id)
        .subquery()
    )

    conditions = []
    if search:
        pattern = f"%{search}%"
        conditions.append(or_(User.email.ilike(pattern), User.display_name.ilike(pattern)))
    if role:
        conditions.append(User.role == role)
    if is_active is not None:
        conditions.append(User.is_active == is_active)

    count_query = select(func.count()).select_from(User)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = await db.scalar(count_query)

    query = (
        select(
            User,
            func.coalesce(sets_count_subq.c.total_sets, 0).label("total_sets"),
            func.coalesce(sessions_count_subq.c.total_sessions, 0).label("total_sessions"),
        )
        .outerjoin(sets_count_subq, sets_count_subq.c.owner_id == User.id)
        .outerjoin(sessions_count_subq, sessions_count_subq.c.user_id == User.id)
    )
    if conditions:
        query = query.where(and_(*conditions))

    sort_column_map = {
        "created_at": User.created_at,
        "streak": User.streak,
        "last_studied": User.last_studied,
    }
    sort_column = sort_column_map.get(sort_by, User.created_at)
    order_func = desc if sort_order == "desc" else asc
    query = query.order_by(order_func(sort_column)).offset((page - 1) * limit).limit(limit)

    rows = (await db.execute(query)).all()

    items = [
        AdminUserListItem(
            id=row.User.id,
            email=row.User.email,
            display_name=row.User.display_name,
            role=row.User.role,
            is_active=row.User.is_active,
            streak=row.User.streak,
            created_at=row.User.created_at,
            last_studied=row.User.last_studied,
            total_sets=row.total_sets,
            total_sessions=row.total_sessions,
        )
        for row in rows
    ]

    return AdminUserListResponse(items=items, total=total or 0, page=page, limit=limit)


async def get_user_detail(db: AsyncSession, user_id: UUID) -> AdminUserDetailResponse:
    user = await db.get(User, user_id)
    if user is None:
        raise _not_found("User")

    total_sets = await db.scalar(
        select(func.count()).select_from(StudySet).where(StudySet.owner_id == user_id)
    )
    total_cards = await db.scalar(
        select(func.count()).select_from(Card).where(Card.owner_id == user_id)
    )
    total_sessions = await db.scalar(
        select(func.count())
        .select_from(StudySession)
        .where(and_(StudySession.user_id == user_id, StudySession.ended_at.is_not(None)))
    )

    device_rows = (
        (
            await db.execute(
                select(RefreshToken)
                .where(RefreshToken.user_id == user_id)
                .order_by(RefreshToken.created_at.desc())
                .limit(10)
            )
        )
        .scalars()
        .all()
    )
    devices = [
        DeviceInfo(
            id=d.id,
            device=d.device,
            ip=str(d.ip) if d.ip else None,
            created_at=d.created_at,
            is_revoked=d.is_revoked,
            expires_at=d.expires_at,
        )
        for d in device_rows
    ]

    session_rows = (
        await db.execute(
            select(StudySession, StudySet.title)
            .join(StudySet, StudySet.id == StudySession.study_set_id)
            .where(and_(StudySession.user_id == user_id, StudySession.ended_at.is_not(None)))
            .order_by(StudySession.ended_at.desc())
            .limit(5)
        )
    ).all()
    recent_sessions = [
        RecentSessionItem(
            id=row.StudySession.id,
            set_title=row.title,
            mode=row.StudySession.mode,
            cards_studied=row.StudySession.cards_studied,
            correct=row.StudySession.correct,
            incorrect=row.StudySession.incorrect,
            ended_at=row.StudySession.ended_at,
        )
        for row in session_rows
    ]

    return AdminUserDetailResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active,
        streak=user.streak,
        last_studied=user.last_studied,
        created_at=user.created_at,
        total_sets=total_sets or 0,
        total_cards=total_cards or 0,
        total_sessions=total_sessions or 0,
        devices=devices,
        recent_sessions=recent_sessions,
    )


async def update_user(
    db: AsyncSession,
    user_id: UUID,
    payload: AdminUserUpdateRequest,
    current_admin_id: UUID,
) -> AdminUserUpdateResponse:
    user = await db.get(User, user_id)
    if user is None:
        raise _not_found("User")

    if (
        payload.is_active is None
        and payload.role is None
        and payload.force_reset_password is None
    ):
        raise _bad_request("No update fields provided")

    temp_password: str | None = None

    if payload.is_active is not None:
        if user.id == current_admin_id and payload.is_active is False:
            raise _bad_request("Cannot deactivate your own account")
        user.is_active = payload.is_active
        if payload.is_active is False:
            await db.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == user_id)
                .values(is_revoked=True)
            )

    if payload.role is not None:
        if payload.role not in ("user", "admin"):
            raise _bad_request("role must be 'user' or 'admin'")
        if user.id == current_admin_id and payload.role == "user":
            raise _bad_request("Cannot revoke your own admin role")
        user.role = payload.role

    if payload.force_reset_password:
        temp_password = secrets.token_urlsafe(9)
        user.password = hash_password(temp_password)
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )

    await db.commit()
    await db.refresh(user)

    return AdminUserUpdateResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        temp_password=temp_password,
    )


async def delete_user(db: AsyncSession, user_id: UUID, current_admin_id: UUID) -> None:
    if user_id == current_admin_id:
        raise _bad_request("Cannot delete your own account")

    user = await db.get(User, user_id)
    if user is None:
        raise _not_found("User")

    await db.delete(user)
    await db.commit()