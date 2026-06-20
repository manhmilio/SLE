from fastapi import APIRouter, Query
from app.dependencies import AdminUser, DB
from app.schemas.admin import DashboardResponse
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: DB,
    current_user: AdminUser,
    range: str = Query(default="7d", pattern="^(7d|30d|90d)$", alias="range"),
):
    return await admin_service.get_dashboard(db=db, range_str=range)