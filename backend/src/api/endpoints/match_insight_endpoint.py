from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_match_insight_service
from src.api.schemas.match_insight import (
    GenerateMatchInsightsRequest,
    MatchInsightResponse,
)
from src.database.models.match_insights import Importance, InsightType
from src.services.match_insight_service import MatchInsightService

match_insight_route = APIRouter(prefix="/api", tags=["Match insights"])


@match_insight_route.post(
    "/matches/{match_id}/insights/generate",
    response_model=list[MatchInsightResponse],
    status_code=status.HTTP_200_OK,
)
async def generate_match_insights(
    match_id: UUID,
    data: GenerateMatchInsightsRequest,
    insight_service: MatchInsightService = Depends(get_match_insight_service),
):
    return await insight_service.generate_match_insights(
        match_id=match_id,
        language=data.language,
        audience=data.audience,
    )


@match_insight_route.get(
    "/matches/{match_id}/insights",
    response_model=list[MatchInsightResponse],
)
async def get_match_insights(
    match_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    insight_type: InsightType | None = None,
    importance: Importance | None = None,
    insight_service: MatchInsightService = Depends(get_match_insight_service),
):
    return await insight_service.get_match_insights(
        match_id=match_id,
        limit=limit,
        offset=offset,
        insight_type=insight_type,
        importance=importance,
    )


@match_insight_route.get(
    "/insights/{insight_id}",
    response_model=MatchInsightResponse,
)
async def get_insight(
    insight_id: UUID,
    insight_service: MatchInsightService = Depends(get_match_insight_service),
):
    return await insight_service.get_insight_by_id(insight_id)
