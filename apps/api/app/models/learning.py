import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, SmallInteger, Text, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class StudyProgress(Base):
    __tablename__ = "study_progress"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    card_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    study_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)

    # SM-2 fields
    ease_factor: Mapped[float] = mapped_column(Float, nullable=False, server_default="2.5")
    interval: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    repetitions: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    next_review: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")
    last_reviewed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    streak: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")

    from sqlalchemy import UniqueConstraint, CheckConstraint
    __table_args__ = (
        UniqueConstraint("user_id", "card_id", "mode", name="uq_progress_user_card_mode"),
        CheckConstraint("mode IN ('flashcard', 'learn', 'test', 'match')", name="ck_progress_mode"),
    )


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    study_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    cards_studied: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    correct: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    incorrect: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    from sqlalchemy import CheckConstraint
    __table_args__ = (
        CheckConstraint("mode IN ('flashcard', 'learn', 'test', 'match')", name="ck_session_mode"),
    )

    answers: Mapped[list["SessionAnswer"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class SessionAnswer(Base):
    __tablename__ = "session_answers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    card_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)

    # Snapshot
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)

    # Kết quả
    user_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_spent: Mapped[int] = mapped_column(Integer, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")

    session: Mapped["StudySession"] = relationship(back_populates="answers")


class SetClone(Base):
    __tablename__ = "set_clones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False)
    original_owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cloned_set_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("study_sets.id", ondelete="CASCADE"), nullable=False)
    cloned_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cloned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="now()")

    from sqlalchemy import UniqueConstraint
    __table_args__ = (
        UniqueConstraint("original_set_id", "cloned_by", name="uq_clone"),
    )