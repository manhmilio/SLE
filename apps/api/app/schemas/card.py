from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CardCreate(BaseModel):
    front: str = Field(..., min_length=1, max_length=2000)
    back: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None


class CardUpdate(BaseModel):
    front: Optional[str] = Field(None, min_length=1, max_length=2000)
    back: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None


class CardResponse(BaseModel):
    id: UUID
    study_set_id: UUID
    owner_id: UUID
    front: str
    back: Optional[str]
    image_url: Optional[str]
    order: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}