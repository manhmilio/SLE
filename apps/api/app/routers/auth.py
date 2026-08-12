"""
routers/auth.py — POST /auth/register · POST /auth/login
Task 2.1 — Auth core
Phase 9.1: refresh token chuyển sang httpOnly cookie thay vì JSON body.
"""
from fastapi import APIRouter, HTTPException, Request, Response, status
from app.schemas.common import SuccessEnvelope, MessageData
from app.core.config import settings

from app.dependencies import DB, CurrentUser
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    UserPublic,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/api/v1/auth"


def _get_client_ip(request: Request) -> str | None:
    """Lấy IP thực của client (hỗ trợ reverse proxy)."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path=COOKIE_PATH)


def _get_refresh_cookie(request: Request) -> str:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": {"code": "MISSING_REFRESH_TOKEN", "message": "Refresh token cookie is missing"}},
        )
    return token


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    response_model=SuccessEnvelope[RegisterResponse],
)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    db: DB,
) -> SuccessEnvelope[RegisterResponse]:
    """
    Tạo tài khoản mới và trả về access token; refresh token được set qua httpOnly cookie.

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
            detail={"success": False, "error": {"code": "EMAIL_TAKEN", "message": str(exc)}},
        )

    _set_refresh_cookie(response, tokens.refresh_token)
    result = RegisterResponse(user=UserPublic.model_validate(user), tokens=tokens)
    return SuccessEnvelope(data=result)


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập",
    response_model=SuccessEnvelope[LoginResponse],
)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: DB,
) -> SuccessEnvelope[LoginResponse]:
    """
    Đăng nhập bằng email + password.
    Trả về access token (JWT); refresh token được set qua httpOnly cookie.
    """
    user = await auth_service.authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": {"code": "INVALID_CREDENTIALS", "message": "Email or password is incorrect"}},
        )

    tokens = await auth_service.login_user(
        db=db, user=user, ip=_get_client_ip(request),
        device=body.device or request.headers.get("User-Agent", "")[:255],
    )

    _set_refresh_cookie(response, tokens.refresh_token)
    result = LoginResponse(user=UserPublic.model_validate(user), tokens=tokens)
    return SuccessEnvelope(data=result)


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------
@router.post("/refresh", summary="Xoay refresh token", response_model=SuccessEnvelope[RefreshResponse])
async def refresh(
    request: Request,
    response: Response,
    db: DB,
) -> SuccessEnvelope[RefreshResponse]:
    raw_token = _get_refresh_cookie(request)
    try:
        tokens = await auth_service.refresh_tokens(db, raw_token)
    except ValueError as exc:
        _clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": {"code": "INVALID_REFRESH_TOKEN", "message": str(exc)}},
        )
    _set_refresh_cookie(response, tokens.refresh_token)
    return SuccessEnvelope(data=RefreshResponse(tokens=tokens))


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------
@router.post("/logout", summary="Đăng xuất thiết bị hiện tại", response_model=SuccessEnvelope[MessageData])
async def logout(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    db: DB,
) -> SuccessEnvelope[MessageData]:
    raw_token = _get_refresh_cookie(request)
    try:
        await auth_service.logout(db, raw_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": {"code": "INVALID_REFRESH_TOKEN", "message": str(exc)}},
        )
    _clear_refresh_cookie(response)
    return SuccessEnvelope(data=MessageData(message="Logged out successfully"))


# ---------------------------------------------------------------------------
# POST /auth/logout-all
# ---------------------------------------------------------------------------
@router.post("/logout-all", summary="Đăng xuất toàn bộ thiết bị", response_model=SuccessEnvelope[MessageData])
async def logout_all(
    response: Response,
    current_user: CurrentUser,
    db: DB,
) -> SuccessEnvelope[MessageData]:
    await auth_service.logout_all(db, str(current_user.id))
    _clear_refresh_cookie(response)
    return SuccessEnvelope(data=MessageData(message="Logged out from all devices"))