from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StatsOverviewResponse(BaseModel):
    streak: int
    last_studied: Optional[datetime]
    total_cards_known: int
    total_cards_learning: int
    total_sessions: int
    total_study_time_seconds: int
    sets_studied: int