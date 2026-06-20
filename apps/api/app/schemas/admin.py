from datetime import datetime

from pydantic import BaseModel
from uuid import UUID
from app.schemas.session import StudyMode

class UserMetrics(BaseModel):
    total: int
    active: int
    inactive: int
    new_today: int
    new_7d: int


class SetMetrics(BaseModel):
    total: int
    public: int
    private: int


class SessionMetrics(BaseModel):
    today: int
    last_7d: int
    last_30d: int


class ActiveUserMetrics(BaseModel):
    dau: int   # Daily Active Users
    mau: int   # Monthly Active Users


class ChartPoint(BaseModel):
    date: str   # "2026-06-19"
    count: int


class DashboardResponse(BaseModel):
    users: UserMetrics
    sets: SetMetrics
    sessions: SessionMetrics
    active_users: ActiveUserMetrics
    user_growth: list[ChartPoint]     # users đăng ký theo ngày
    session_chart: list[ChartPoint]   # sessions theo ngày


# ─────────────────────────── List Users ───────────────────────────

class AdminUserListItem(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: str
    is_active: bool
    streak: int
    created_at: datetime
    last_studied: datetime | None
    total_sets: int
    total_sessions: int


class AdminUserListResponse(BaseModel):
    items: list[AdminUserListItem]
    total: int
    page: int
    limit: int


# ─────────────────────────── User Detail ───────────────────────────

class DeviceInfo(BaseModel):
    id: UUID
    device: str | None
    ip: str | None
    created_at: datetime
    is_revoked: bool
    expires_at: datetime


class RecentSessionItem(BaseModel):
    id: UUID
    set_title: str
    mode: StudyMode
    cards_studied: int
    correct: int
    incorrect: int
    ended_at: datetime | None


class AdminUserDetailResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    avatar_url: str | None
    role: str
    is_active: bool
    streak: int
    last_studied: datetime | None
    created_at: datetime
    total_sets: int
    total_cards: int
    total_sessions: int
    devices: list[DeviceInfo]
    recent_sessions: list[RecentSessionItem]


# ─────────────────────────── Update User ───────────────────────────

class AdminUserUpdateRequest(BaseModel):
    is_active: bool | None = None
    role: str | None = None
    force_reset_password: bool | None = None


class AdminUserUpdateResponse(BaseModel):
    id: UUID
    email: str
    role: str
    is_active: bool
    temp_password: str | None = None