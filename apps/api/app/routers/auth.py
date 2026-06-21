"""
routers/auth.py — POST /auth/register · POST /auth/login
Task 2.1 — Auth core
"""
from fastapi import APIRouter, HTTPException, Request, status

from app.dependencies import DB, CurrentUser
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest, 
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    UserPublic, 
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_client_ip(request: Request) -> str | None:
    """Lấy IP thực của client (hỗ trợ reverse proxy)."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
)
async def register(
    body: RegisterRequest,
    request: Request,
    db: DB,
) -> dict:
    """
    Tạo tài khoản mới và trả về access + refresh token ngay lập tức.

    - **email**: định dạng email hợp lệ, unique
    - **password**: tối thiểu 8 ký tự, phải có chữ và số
    - **display_name**: tên hiển thị, 1-100 ký tự
    """
    try:
        user, tokens = await auth_service.register_user(
            db=db,
            data=body,
            ip=_get_client_ip(request),
            device=request.headers.get("User-Agent", "")[:255],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error": {
                    "code": "EMAIL_TAKEN",
                    "message": str(exc),
                },
            },
        )

    response = RegisterResponse(
        user=UserPublic.model_validate(user),
        tokens=tokens,
    )
    return {"success": True, "data": response.model_dump()}


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập",
)
async def login(
    body: LoginRequest,
    request: Request,
    db: DB,
) -> dict:
    """
    Đăng nhập bằng email + password.
    Trả về access token (JWT) và refresh token (opaque).
    """
    user = await auth_service.authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Email or password is incorrect",
                },
            },
        )

    tokens = await auth_service.login_user(
        db=db,
        user=user,
        ip=_get_client_ip(request),
        device=body.device or request.headers.get("User-Agent", "")[:255],
    )

    response = LoginResponse(
        user=UserPublic.model_validate(user),
        tokens=tokens,
    )
    return {"success": True, "data": response.model_dump()}

# POST /auth/refresh
@router.post("/refresh", summary="Xoay refresh token")
async def refresh(body: RefreshRequest, db: DB) -> dict:
    try:
        tokens = await auth_service.refresh_tokens(db, body.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {"code": "INVALID_REFRESH_TOKEN", "message": str(exc)},
            },
        )
    return {"success": True, "data": RefreshResponse(tokens=tokens).model_dump()}

# POST /auth/logout
@router.post("/logout", summary="Đăng xuất thiết bị hiện tại")
async def logout(
    body: RefreshRequest,
    current_user: CurrentUser,
    db: DB,
) -> dict:
    try:
        await auth_service.logout(db, body.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {"code": "INVALID_REFRESH_TOKEN", "message": str(exc)},
            },
        )
    return {"success": True, "data": {"message": "Logged out successfully"}}

# POST /auth/logout-all
@router.post("/logout-all", summary="Đăng xuất toàn bộ thiết bị")
async def logout_all(current_user: CurrentUser, db: DB) -> dict:
    await auth_service.logout_all(db, str(current_user.id))
    return {"success": True, "data": {"message": "Logged out from all devices"}}