from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_analytics_service
from src.services.analytics_service import AnalyticsService

analytics_route = APIRouter(prefix="/api/matches", tags=["Analytics"])


@analytics_route.get("/{match_id}/analytics")
async def get_match_analytics(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.run_match_analysis(match_id)
