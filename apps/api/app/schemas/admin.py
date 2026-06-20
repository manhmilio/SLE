from pydantic import BaseModel


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