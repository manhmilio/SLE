from __future__ import annotations
from fastapi import APIRouter, Query
from typing import Literal

from app.dependencies import CurrentUser, DB
from app.schemas.stats import StatsOverviewResponse, SessionHistoryResponse
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverviewResponse)
async def get_stats_overview(
    current_user: CurrentUser,
    db: DB,
) -> StatsOverviewResponse:
    return await stats_service.get_overview(db, current_user.id)


@router.get("/sessions", response_model=SessionHistoryResponse)
async def get_sessions_history(
    current_user: CurrentUser,
    db: DB,
    time_range: Literal["7d", "30d", "90d"] = Query(default="7d", alias="range"),
    group_by: Literal["day", "week"] = Query(default="day"),
) -> SessionHistoryResponse:
    return await stats_service.get_sessions_history(
        db, current_user.id, time_range, group_by
    )