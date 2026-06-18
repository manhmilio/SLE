from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import Literal


class StatsOverviewResponse(BaseModel):
    streak: int
    last_studied: Optional[datetime]
    total_cards_known: int
    total_cards_learning: int
    total_sessions: int
    total_study_time_seconds: int
    sets_studied: int

class SessionHistoryItem(BaseModel):
    date: str                   # "2026-06-11"
    sessions: int
    cards_studied: int
    correct: int
    incorrect: int
    accuracy: float             # 0.0 nếu không có card nào
    study_time_seconds: int


class SessionHistoryResponse(BaseModel):
    range: str
    group_by: str
    data: list[SessionHistoryItem]