from datetime import datetime
from sqlalchemy import Integer, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    initial_ease_factor: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    min_ease_factor: Mapped[float] = mapped_column(Float, nullable=False, default=1.3)
    known_threshold_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    max_sets_per_user: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    max_cards_per_set: Mapped[int] = mapped_column(Integer, nullable=False, default=500)
    max_image_size_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    allow_registration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)