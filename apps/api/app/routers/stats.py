from __future__ import annotations
from fastapi import APIRouter

from app.dependencies import CurrentUser, DB
from app.schemas.stats import StatsOverviewResponse
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverviewResponse)
async def get_stats_overview(
    current_user: CurrentUser,
    db: DB,
) -> StatsOverviewResponse:
    return await stats_service.get_overview(db, current_user.id)