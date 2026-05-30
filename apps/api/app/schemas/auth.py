"""
schemas/auth.py — Request & Response schemas cho /auth endpoints
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)  # bỏ validator strength, chỉ giữ length
    display_name: str = Field(min_length=1, max_length=100)

    @field_validator("display_name")
    @classmethod
    def display_name_strip(cls, v: str) -> str:
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device: str | None = Field(default=None, max_length=255)

# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------
class UserPublic(BaseModel):
    """Thông tin user trả về trong response — không có password."""
    id: UUID
    email: str
    display_name: str
    avatar_url: str | None
    role: str
    is_active: bool
    streak: int
    last_studied: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int          # seconds until access token expires


class RegisterResponse(BaseModel):
    user: UserPublic
    tokens: TokenData


class LoginResponse(BaseModel):
    user: UserPublic
    tokens: TokenData

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    tokens: TokenData