from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class StudySetCreate(BaseModel):
    title: str
    description: Optional[str] = None
    folder_id: Optional[UUID] = None
    tags: List[str] = []
    is_public: bool = False

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v


class StudySetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    folder_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

    @field_validator("title", mode="before")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = str(v).strip()
            if not v:
                raise ValueError("Title cannot be empty")
        return v


class StudySetResponse(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: Optional[str] = None
    folder_id: Optional[UUID] = None
    tags: List[str]
    is_public: bool
    card_count: int
    cloned_from: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}