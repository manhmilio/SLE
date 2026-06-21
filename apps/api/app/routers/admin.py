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
    AdminSetListResponse,
    AdminSetUpdateRequest,
    AdminSetUpdateResponse,
    AdminUserStatsResponse,
    AdminLearningStatsResponse,
    AdminContentStatsResponse,
    SystemConfigResponse,
    SystemConfigUpdateRequest,
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


@router.get("/sets", response_model=AdminSetListResponse)
async def list_sets(
    db: DB,
    current_user: AdminUser,
    owner_id: UUID | None = Query(default=None),
    is_public: bool | None = Query(default=None),
    sort_by: str = Query(
        default="created_at",
        pattern="^(created_at|session_count|clone_count|card_count)$",
    ),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await admin_service.get_sets_list(
        db=db,
        owner_id=owner_id,
        is_public=is_public,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )


@router.patch("/sets/{set_id}", response_model=AdminSetUpdateResponse)
async def update_set(
    set_id: UUID,
    payload: AdminSetUpdateRequest,
    db: DB,
    current_user: AdminUser,
):
    return await admin_service.update_set(db=db, set_id=set_id, payload=payload)


@router.delete("/sets/{set_id}", status_code=204)
async def delete_set(
    set_id: UUID,
    db: DB,
    current_user: AdminUser,
):
    await admin_service.delete_set(db=db, set_id=set_id)


@router.get("/stats/users", response_model=AdminUserStatsResponse)
async def get_user_stats(
    db: DB,
    current_user: AdminUser,
    range: str = Query(default="30d", pattern="^(7d|30d|90d)$", alias="range"),
):
    return await admin_service.get_user_stats(db=db, range_str=range)


@router.get("/stats/learning", response_model=AdminLearningStatsResponse)
async def get_learning_stats(
    db: DB,
    current_user: AdminUser,
    range: str = Query(default="30d", pattern="^(7d|30d|90d)$", alias="range"),
):
    return await admin_service.get_learning_stats(db=db, range_str=range)


@router.get("/stats/content", response_model=AdminContentStatsResponse)
async def get_content_stats(
    db: DB,
    current_user: AdminUser,
):
    return await admin_service.get_content_stats(db=db)


@router.get("/config", response_model=SystemConfigResponse)
async def get_config(
    db: DB,
    current_user: AdminUser,
):
    return await admin_service.get_config(db=db)


@router.patch("/config", response_model=SystemConfigResponse)
async def update_config(
    payload: SystemConfigUpdateRequest,
    db: DB,
    current_user: AdminUser,
):
    return await admin_service.update_config(db=db, payload=payload)