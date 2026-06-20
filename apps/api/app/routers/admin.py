from fastapi import APIRouter, Query
from app.dependencies import AdminUser, DB
# from app.schemas.admin import DashboardResponse
from app.services import admin_service
from uuid import UUID
from app.schemas.admin import (
    DashboardResponse,
    AdminUserListResponse,
    AdminUserDetailResponse,
    AdminUserUpdateRequest,
    AdminUserUpdateResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: DB,
    current_user: AdminUser,
    range: str = Query(default="7d", pattern="^(7d|30d|90d)$", alias="range"),
):
    return await admin_service.get_dashboard(db=db, range_str=range)


@router.get("/users", response_model=AdminUserListResponse)
async def list_users(
    db: DB,
    current_user: AdminUser,
    search: str | None = Query(default=None),
    role: str | None = Query(default=None, pattern="^(user|admin)$"),
    is_active: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at", pattern="^(created_at|streak|last_studied)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await admin_service.get_users_list(
        db=db,
        search=search,
        role=role,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )


@router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
async def get_user_detail(
    user_id: UUID,
    db: DB,
    current_user: AdminUser,
):
    return await admin_service.get_user_detail(db=db, user_id=user_id)


@router.patch("/users/{user_id}", response_model=AdminUserUpdateResponse)
async def update_user(
    user_id: UUID,
    payload: AdminUserUpdateRequest,
    db: DB,
    current_user: AdminUser,
):
    return await admin_service.update_user(
        db=db, user_id=user_id, payload=payload, current_admin_id=current_user.id
    )


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: DB,
    current_user: AdminUser,
):
    await admin_service.delete_user(db=db, user_id=user_id, current_admin_id=current_user.id)