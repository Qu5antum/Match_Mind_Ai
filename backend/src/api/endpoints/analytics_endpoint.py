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


@analytics_route.get("/{match_id}/analytics/statistics")
async def get_match_statistics(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_match_statistics(match_id)


@analytics_route.get("/{match_id}/analytics/teams/{team_id}")
async def get_team_statistics(
    match_id: UUID,
    team_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_team_statistics(match_id, team_id)


@analytics_route.get("/{match_id}/analytics/players/{player_id}")
async def get_player_statistics(
    match_id: UUID,
    player_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_player_statistics(match_id, player_id)


@analytics_route.get("/{match_id}/analytics/shots")
async def get_shot_statistics(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_shot_statistics(match_id)


@analytics_route.get("/{match_id}/analytics/key-moments")
async def get_key_moments(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.detect_key_moments(match_id)


@analytics_route.get("/{match_id}/analytics/possession")
async def get_possession_statistics(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.calculate_possession_statistics(match_id)


@analytics_route.get("/{match_id}/analytics/team-performance")
async def get_team_performance_comparison(
    match_id: UUID,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    return await analytics_service.analyze_team_performance(match_id)
