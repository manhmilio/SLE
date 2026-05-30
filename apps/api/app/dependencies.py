"""
dependencies.py — FastAPI dependencies dùng chung cho toàn app
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services.auth_service import get_user_by_id

# Bearer scheme — tự động đọc header "Authorization: Bearer <token>"
_bearer = HTTPBearer(auto_error=False)

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={
        "success": False,
        "error": {
            "code": "UNAUTHORIZED",
            "message": "Could not validate credentials",
        },
    },
    headers={"WWW-Authenticate": "Bearer"},
)

_INACTIVE_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={
        "success": False,
        "error": {
            "code": "ACCOUNT_DISABLED",
            "message": "Your account has been disabled",
        },
    },
)

_ADMIN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={
        "success": False,
        "error": {
            "code": "FORBIDDEN",
            "message": "Admin access required",
        },
    },
)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency: xác thực JWT, trả về User đang đăng nhập.
    Raise 401 nếu token không hợp lệ / hết hạn.
    Raise 403 nếu account bị disabled.
    """
    if not credentials:
        raise _CREDENTIALS_EXCEPTION

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise _CREDENTIALS_EXCEPTION
    except JWTError:
        raise _CREDENTIALS_EXCEPTION

    user = await get_user_by_id(db, user_id)
    if not user:
        raise _CREDENTIALS_EXCEPTION
    if not user.is_active:
        raise _INACTIVE_EXCEPTION

    return user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency: yêu cầu user phải có role = 'admin'.
    Dùng cho tất cả /admin/* endpoints ở Phase 8.
    """
    if current_user.role != "admin":
        raise _ADMIN_EXCEPTION
    return current_user


# ---------------------------------------------------------------------------
# Convenient type aliases (dùng trong route signatures)
# ---------------------------------------------------------------------------
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
DB = Annotated[AsyncSession, Depends(get_db)]