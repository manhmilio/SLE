"""
services/auth_service.py — Business logic cho authentication
"""
from datetime import timedelta, timezone, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import RefreshToken, User
from app.schemas.auth import RegisterRequest, TokenData


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def _build_token_data(raw_access: str, raw_refresh: str) -> TokenData:
    return TokenData(
        access_token=raw_access,
        refresh_token=raw_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------
async def register_user(
    db: AsyncSession,
    data: RegisterRequest,
    ip: str | None = None,
    device: str | None = None,
) -> tuple[User, TokenData]:
    """
    Tạo user mới, issue access + refresh token.
    Raises ValueError nếu email đã tồn tại.
    """
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise ValueError("Email already registered")

    user = User(
        email=data.email.lower(),
        password=hash_password(data.password),
        display_name=data.display_name.strip(),
    )
    db.add(user)
    await db.flush()   # lấy user.id trước khi commit

    tokens = await _issue_tokens(db, user, ip=ip, device=device)
    await db.commit()
    await db.refresh(user)
    return user, tokens


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Trả về User nếu đúng email + password, None nếu sai."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    if not user.is_active:
        return None
    return user


async def login_user(
    db: AsyncSession,
    user: User,
    ip: str | None = None,
    device: str | None = None,
) -> TokenData:
    """Issue tokens cho user đã xác thực."""
    tokens = await _issue_tokens(db, user, ip=ip, device=device)
    await db.commit()
    return tokens


# ---------------------------------------------------------------------------
# Internal — issue tokens
# ---------------------------------------------------------------------------
async def _issue_tokens(
    db: AsyncSession,
    user: User,
    ip: str | None,
    device: str | None,
) -> TokenData:
    # Access token
    raw_access, _expires_at = create_access_token(
        subject=str(user.id),
        role=user.role,
    )

    # Refresh token — lưu hashed vào DB
    raw_refresh, hashed_refresh = generate_refresh_token()
    refresh_expires = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    db_token = RefreshToken(
        user_id=user.id,
        token=hashed_refresh,
        device=device,
        ip=ip,
        expires_at=refresh_expires,
    )
    db.add(db_token)

    return _build_token_data(raw_access, raw_refresh)