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


class ProgressSummary(BaseModel):
    known: int
    learning: int
    not_started: int
    known_rate: float           # % so với tổng cards trong set


class ModeStats(BaseModel):
    mode: str
    sessions: int
    avg_accuracy: float
    last_studied: Optional[datetime]


class SetStatsResponse(BaseModel):
    set_id: str
    set_title: str
    card_count: int
    progress_summary: ProgressSummary
    by_mode: list[ModeStats]
    total_sessions: int
    total_study_time_seconds: int