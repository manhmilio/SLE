"""
core/security.py — JWT & password hashing utilities
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# Access token (JWT)
# ---------------------------------------------------------------------------
def create_access_token(
    subject: str,           # user_id (UUID string)
    role: str,
    expires_delta: timedelta | None = None,
) -> tuple[str, datetime]:
    """Return (encoded_jwt, expires_at)."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT.
    Raises jose.JWTError on failure — caller handles the exception.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != "access":
        raise JWTError("Not an access token")
    return payload


# ---------------------------------------------------------------------------
# Refresh token (opaque random string stored hashed in DB)
# ---------------------------------------------------------------------------
def generate_refresh_token() -> tuple[str, str]:
    """Return (raw_token, hashed_token). Store hashed; send raw to client."""
    raw = secrets.token_urlsafe(64)
    hashed = _hash_token(raw)
    return raw, hashed


def hash_refresh_token(raw: str) -> str:
    return _hash_token(raw)


def _hash_token(raw: str) -> str:
    """SHA-256 hash — fast, non-reversible, safe for DB storage."""
    return hashlib.sha256(raw.encode()).hexdigest()