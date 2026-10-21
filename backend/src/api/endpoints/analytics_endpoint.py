from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_analytics_service
from src.api.schemas.analytics_schema import (
    KeyMomentResponse,
    MatchAnalyticsResponse,
    MatchStatisticsResponse,
    PlayerMatchStatisticsResponse,
    PossessionStatisticsResponse,
    ShotStatisticsResponse,
    TeamPerformanceComparisonResponse,
    TeamStatisticsOnlyResponse,
)
from src.services.analytics_service import AnalyticsService

analytics_route = APIRouter(prefix="/api/matches", tags=["Analytics"])


@analytics_route.get(
    "/{match_id}/analytics",
    response_model=MatchAnalyticsResponse,
)
async def get_match_analytics(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.run_match_analysis(match_id)


@analytics_route.get(
    "/{match_id}/analytics/statistics",
    response_model=MatchStatisticsResponse,
)
async def get_match_statistics(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_match_statistics(match_id)


@analytics_route.get(
    "/{match_id}/analytics/teams/{team_id}",
    response_model=TeamStatisticsOnlyResponse,
)
async def get_team_statistics(
    match_id: UUID,
    team_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_team_statistics(match_id, team_id)


@analytics_route.get(
    "/{match_id}/analytics/players/{player_id}",
    response_model=PlayerMatchStatisticsResponse,
)
async def get_player_statistics(
    match_id: UUID,
    player_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_player_statistics(match_id, player_id)


@analytics_route.get(
    "/{match_id}/analytics/shots",
    response_model=dict[str, ShotStatisticsResponse],
)
async def get_shot_statistics(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_shot_statistics(match_id)


@analytics_route.get(
    "/{match_id}/analytics/key-moments",
    response_model=list[KeyMomentResponse],
)
async def get_key_moments(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.detect_key_moments(match_id)


@analytics_route.get(
    "/{match_id}/analytics/possession",
    response_model=PossessionStatisticsResponse,
)
async def get_possession_statistics(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_possession_statistics(match_id)


@analytics_route.get(
    "/{match_id}/analytics/team-performance",
    response_model=TeamPerformanceComparisonResponse,
)
async def get_team_performance_comparison(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.analyze_team_performance(match_id)
