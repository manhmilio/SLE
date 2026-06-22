from datetime import datetime, date, timedelta, timezone
from sqlalchemy import select, func, distinct, and_
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
from uuid import UUID
from sqlalchemy import select, func, distinct, and_, or_, update, desc, asc
from fastapi import HTTPException, status as http_status
from app.core.security import hash_password
from app.services.config_service import get_current_config
from app.models.config import SystemConfig


from app.models.user import User
from app.models.content import StudySet
from app.models.learning import StudySession, SetClone, StudyProgress
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
    AdminSetListItem,
    AdminSetListResponse,
    AdminSetUpdateRequest,
    AdminSetUpdateResponse,
    StreakBucket,
    AdminUserStatsResponse,
    ModeDistributionItem,
    AdminLearningStatsResponse,
    TopSetItem,
    TagPopularity,
    AdminContentStatsResponse,
    SystemConfigResponse, 
    SystemConfigUpdateRequest,
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


# ═══════════════════════ Set Management ═══════════════════════

async def get_sets_list(
    db: AsyncSession,
    owner_id: UUID | None,
    is_public: bool | None,
    sort_by: str,
    sort_order: str,
    page: int,
    limit: int,
) -> AdminSetListResponse:
    sessions_count_subq = (
        select(
            StudySession.study_set_id,
            func.count(StudySession.id).label("total_sessions"),
        )
        .where(StudySession.ended_at.is_not(None))
        .group_by(StudySession.study_set_id)
        .subquery()
    )
    clones_count_subq = (
        select(
            SetClone.original_set_id,
            func.count(SetClone.id).label("total_clones"),
        )
        .group_by(SetClone.original_set_id)
        .subquery()
    )

    conditions = []
    if owner_id is not None:
        conditions.append(StudySet.owner_id == owner_id)
    if is_public is not None:
        conditions.append(StudySet.is_public == is_public)

    count_query = select(func.count()).select_from(StudySet)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = await db.scalar(count_query)

    query = (
        select(
            StudySet,
            User.email.label("owner_email"),
            func.coalesce(sessions_count_subq.c.total_sessions, 0).label("total_sessions"),
            func.coalesce(clones_count_subq.c.total_clones, 0).label("total_clones"),
        )
        .join(User, User.id == StudySet.owner_id)
        .outerjoin(sessions_count_subq, sessions_count_subq.c.study_set_id == StudySet.id)
        .outerjoin(clones_count_subq, clones_count_subq.c.original_set_id == StudySet.id)
    )
    if conditions:
        query = query.where(and_(*conditions))

    order_func = desc if sort_order == "desc" else asc
    if sort_by == "session_count":
        order_col = func.coalesce(sessions_count_subq.c.total_sessions, 0)
    elif sort_by == "clone_count":
        order_col = func.coalesce(clones_count_subq.c.total_clones, 0)
    elif sort_by == "card_count":
        order_col = StudySet.card_count
    else:
        order_col = StudySet.created_at

    query = query.order_by(order_func(order_col)).offset((page - 1) * limit).limit(limit)

    rows = (await db.execute(query)).all()

    items = [
        AdminSetListItem(
            id=row.StudySet.id,
            title=row.StudySet.title,
            owner_email=row.owner_email,
            is_public=row.StudySet.is_public,
            card_count=row.StudySet.card_count,
            total_sessions=row.total_sessions,
            total_clones=row.total_clones,
            created_at=row.StudySet.created_at,
        )
        for row in rows
    ]

    return AdminSetListResponse(items=items, total=total or 0, page=page, limit=limit)


async def update_set(
    db: AsyncSession, set_id: UUID, payload: AdminSetUpdateRequest
) -> AdminSetUpdateResponse:
    study_set = await db.get(StudySet, set_id)
    if study_set is None:
        raise _not_found("Study set")

    study_set.is_public = payload.is_public
    await db.commit()
    await db.refresh(study_set)

    return AdminSetUpdateResponse(
        id=study_set.id, title=study_set.title, is_public=study_set.is_public
    )


async def delete_set(db: AsyncSession, set_id: UUID) -> None:
    study_set = await db.get(StudySet, set_id)
    if study_set is None:
        raise _not_found("Study set")

    await db.delete(study_set)
    await db.commit()


# ═══════════════════════ Admin Stats ═══════════════════════

async def get_user_stats(db: AsyncSession, range_str: str = "30d") -> AdminUserStatsResponse:
    today = _today_utc()
    days = VALID_RANGES.get(range_str, 30)
    start_date = today - timedelta(days=days - 1)
    start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)

    growth_trunc = func.date_trunc("day", User.created_at)
    growth_rows = (
        await db.execute(
            select(growth_trunc.label("day"), func.count().label("cnt"))
            .where(User.created_at >= start_dt)
            .group_by(growth_trunc)
            .order_by(growth_trunc)
        )
    ).all()
    growth_map = {row.day.date().isoformat(): row.cnt for row in growth_rows}
    growth: list[ChartPoint] = []
    current = start_date
    while current <= today:
        growth.append(ChartPoint(date=current.isoformat(), count=growth_map.get(current.isoformat(), 0)))
        current += timedelta(days=1)

    all_streaks = (await db.execute(select(User.streak))).scalars().all()
    bucket_counts = {"0": 0, "1-7": 0, "8-30": 0, "30+": 0}
    for s in all_streaks:
        if s == 0:
            bucket_counts["0"] += 1
        elif s <= 7:
            bucket_counts["1-7"] += 1
        elif s <= 30:
            bucket_counts["8-30"] += 1
        else:
            bucket_counts["30+"] += 1
    streak_distribution = [StreakBucket(label=k, count=v) for k, v in bucket_counts.items()]

    total_users = await db.scalar(select(func.count()).select_from(User))
    cutoff = _now_utc() - timedelta(days=30)
    churned = await db.scalar(
        select(func.count())
        .select_from(User)
        .where(
            or_(
                and_(User.last_studied.is_not(None), User.last_studied < cutoff),
                and_(User.last_studied.is_(None), User.created_at < cutoff),
            )
        )
    )
    churn_rate = round((churned or 0) / total_users * 100, 2) if total_users else 0.0

    return AdminUserStatsResponse(
        growth=growth,
        streak_distribution=streak_distribution,
        churn_rate=churn_rate,
    )


async def get_learning_stats(db: AsyncSession, range_str: str = "30d") -> AdminLearningStatsResponse:
    config = await get_current_config(db)
    today = _today_utc()
    days = VALID_RANGES.get(range_str, 30)
    start_date = today - timedelta(days=days - 1)
    start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)

    sess_trunc = func.date_trunc("day", StudySession.created_at)
    sess_rows = (
        await db.execute(
            select(sess_trunc.label("day"), func.count().label("cnt"))
            .where(and_(StudySession.ended_at.is_not(None), StudySession.created_at >= start_dt))
            .group_by(sess_trunc)
            .order_by(sess_trunc)
        )
    ).all()
    sess_map = {row.day.date().isoformat(): row.cnt for row in sess_rows}
    sessions_chart: list[ChartPoint] = []
    current = start_date
    while current <= today:
        sessions_chart.append(ChartPoint(date=current.isoformat(), count=sess_map.get(current.isoformat(), 0)))
        current += timedelta(days=1)

    mode_rows = (
        await db.execute(
            select(
                StudySession.mode,
                func.count().label("sessions"),
                func.avg(
                    StudySession.correct * 100.0 / func.greatest(StudySession.cards_studied, 1)
                ).label("avg_accuracy"),
            )
            .where(StudySession.ended_at.is_not(None))
            .group_by(StudySession.mode)
        )
    ).all()
    mode_distribution = [
        ModeDistributionItem(
            mode=row.mode,
            sessions=row.sessions,
            avg_accuracy=round(float(row.avg_accuracy or 0), 2),
        )
        for row in mode_rows
    ]

    max_interval_subq = (
        select(
            StudyProgress.user_id,
            StudyProgress.card_id,
            func.max(StudyProgress.interval).label("max_interval"),
        )
        .group_by(StudyProgress.user_id, StudyProgress.card_id)
        .subquery()
    )
    total_progress_cards = await db.scalar(select(func.count()).select_from(max_interval_subq))
    known_cards = await db.scalar(
        select(func.count())
        .select_from(max_interval_subq)
        .where(max_interval_subq.c.max_interval >= config.known_threshold_days)
    )
    avg_known_rate = round((known_cards or 0) / total_progress_cards * 100, 2) if total_progress_cards else 0.0

    overall_avg_accuracy = await db.scalar(
        select(
            func.avg(StudySession.correct * 100.0 / func.greatest(StudySession.cards_studied, 1))
        ).where(StudySession.ended_at.is_not(None))
    )

    return AdminLearningStatsResponse(
        sessions_chart=sessions_chart,
        mode_distribution=mode_distribution,
        avg_known_rate=avg_known_rate,
        avg_accuracy=round(float(overall_avg_accuracy or 0), 2),
    )


async def get_content_stats(db: AsyncSession) -> AdminContentStatsResponse:
    sessions_count_subq = (
        select(StudySession.study_set_id, func.count(StudySession.id).label("cnt"))
        .where(StudySession.ended_at.is_not(None))
        .group_by(StudySession.study_set_id)
        .subquery()
    )
    top_sessions_rows = (
        await db.execute(
            select(StudySet.id, StudySet.title, User.email, sessions_count_subq.c.cnt)
            .join(sessions_count_subq, sessions_count_subq.c.study_set_id == StudySet.id)
            .join(User, User.id == StudySet.owner_id)
            .order_by(sessions_count_subq.c.cnt.desc())
            .limit(10)
        )
    ).all()
    top_sets_by_sessions = [
        TopSetItem(id=row.id, title=row.title, owner_email=row.email, value=row.cnt)
        for row in top_sessions_rows
    ]

    clones_count_subq = (
        select(SetClone.original_set_id, func.count(SetClone.id).label("cnt"))
        .group_by(SetClone.original_set_id)
        .subquery()
    )
    top_clones_rows = (
        await db.execute(
            select(StudySet.id, StudySet.title, User.email, clones_count_subq.c.cnt)
            .join(clones_count_subq, clones_count_subq.c.original_set_id == StudySet.id)
            .join(User, User.id == StudySet.owner_id)
            .order_by(clones_count_subq.c.cnt.desc())
            .limit(10)
        )
    ).all()
    top_sets_by_clones = [
        TopSetItem(id=row.id, title=row.title, owner_email=row.email, value=row.cnt)
        for row in top_clones_rows
    ]

    tag_subq = (
        select(func.unnest(StudySet.tags).label("tag")).where(StudySet.is_public.is_(True))
    ).subquery()
    tag_rows = (
        await db.execute(
            select(tag_subq.c.tag, func.count().label("cnt"))
            .group_by(tag_subq.c.tag)
            .order_by(func.count().desc())
            .limit(10)
        )
    ).all()
    popular_tags = [TagPopularity(tag=row.tag, count=row.cnt) for row in tag_rows]

    return AdminContentStatsResponse(
        top_sets_by_sessions=top_sets_by_sessions,
        top_sets_by_clones=top_sets_by_clones,
        popular_tags=popular_tags,
    )


# ═══════════════════════ System Config ═══════════════════════

CONFIG_ROW_ID = 1


async def get_config(db: AsyncSession) -> SystemConfigResponse:
    config = await db.get(SystemConfig, CONFIG_ROW_ID)
    if config is None:
        raise _not_found("System config")

    return SystemConfigResponse(
        initial_ease_factor=config.initial_ease_factor,
        min_ease_factor=config.min_ease_factor,
        known_threshold_days=config.known_threshold_days,
        max_sets_per_user=config.max_sets_per_user,
        max_cards_per_set=config.max_cards_per_set,
        max_image_size_mb=config.max_image_size_mb,
        allow_registration=config.allow_registration,
        updated_at=config.updated_at,
    )


async def update_config(
    db: AsyncSession, payload: SystemConfigUpdateRequest
) -> SystemConfigResponse:
    config = await db.get(SystemConfig, CONFIG_ROW_ID)
    if config is None:
        raise _not_found("System config")

    update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise _bad_request("No update fields provided")

    if "min_ease_factor" in update_data or "initial_ease_factor" in update_data:
        new_min = update_data.get("min_ease_factor", config.min_ease_factor)
        new_initial = update_data.get("initial_ease_factor", config.initial_ease_factor)
        if new_min > new_initial:
            raise _bad_request("min_ease_factor cannot be greater than initial_ease_factor")

    for field, value in update_data.items():
        setattr(config, field, value)
    config.updated_at = _now_utc()

    await db.commit()
    await db.refresh(config)

    return SystemConfigResponse(
        initial_ease_factor=config.initial_ease_factor,
        min_ease_factor=config.min_ease_factor,
        known_threshold_days=config.known_threshold_days,
        max_sets_per_user=config.max_sets_per_user,
        max_cards_per_set=config.max_cards_per_set,
        max_image_size_mb=config.max_image_size_mb,
        allow_registration=config.allow_registration,
        updated_at=config.updated_at,
    )