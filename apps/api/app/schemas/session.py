from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────
from enum import Enum


class StudyMode(str, Enum):
    flashcard = "flashcard"
    learn = "learn"
    test = "test"
    match = "match"


class CardStatus(str, Enum):
    not_started = "not_started"
    learning = "learning"
    known = "known"


# ── POST /sessions ─────────────────────────────────────────────────────────────
class SessionCreate(BaseModel):
    set_id: UUID
    mode: StudyMode


class CardInSession(BaseModel):
    """Thông tin card trả về khi tạo session."""
    id: UUID
    front: str
    back: str
    image_url: Optional[str] = None
    order: float
    # SM-2 state hiện tại (None nếu chưa học lần nào)
    next_review: Optional[datetime] = None
    status: CardStatus = CardStatus.not_started

    model_config = {"from_attributes": True}


class SessionCreateResponse(BaseModel):
    id: UUID
    set_id: UUID
    mode: StudyMode
    started_at: datetime
    cards: list[CardInSession]

    model_config = {"from_attributes": True}


# ── POST /sessions/:id/answers ─────────────────────────────────────────────────
class AnswerSubmit(BaseModel):
    card_id: UUID
    is_correct: bool
    quality: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Bắt buộc nếu mode=learn (1–5). Các mode khác bỏ trống."
    )
    user_answer: Optional[str] = Field(
        default=None,
        description="Text user nhập vào — chỉ dùng cho mode=test."
    )
    time_spent: int = Field(
        ge=0,
        description="Thời gian trả lời tính bằng milliseconds."
    )


class SM2Result(BaseModel):
    """Kết quả SM-2 sau khi tính toán."""
    ease_factor: float
    interval: int
    repetitions: int
    next_review: datetime
    status: CardStatus


class AnswerResponse(BaseModel):
    card_id: UUID
    is_correct: bool
    quality: int
    sm2: SM2Result


# ── POST /sessions/:id/end ─────────────────────────────────────────────────────
class SessionEndResponse(BaseModel):
    id: UUID
    set_id: UUID
    mode: StudyMode
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    cards_studied: int
    correct: int
    incorrect: int
    accuracy: float = Field(description="Phần trăm đúng, 0.0–100.0")

    model_config = {"from_attributes": True}


# ── GET /sessions ──────────────────────────────────────────────────────────────
class SessionListItem(BaseModel):
    id: UUID
    set_id: UUID
    set_title: str
    mode: StudyMode
    started_at: datetime
    ended_at: datetime
    cards_studied: int
    correct: int
    incorrect: int
    accuracy: float

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    items: list[SessionListItem]
    total: int
    page: int
    limit: int