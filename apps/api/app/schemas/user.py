from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserProfile(BaseModel):
    id: UUID
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    role: str
    streak: int
    last_studied: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)