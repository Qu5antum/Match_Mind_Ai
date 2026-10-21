from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_agent_service
from src.api.schemas.agent_schema import (
    AgentSummaryRequest,
    GeneratedInsightExplanation,
    InsightPersonalizationRequest,
    InsightPersonalizationResponse,
    KeyMomentExplanation,
    KeyMomentRequest,
    MatchQuestionRequest,
    MatchQuestionResponse,
    MatchSummaryResponse,
    PlayerAnalysisRequest,
    PlayerAnalysisResponse,
    TacticalAnalysisRequest,
    TacticalAnalysisResponse,
    TeamComparisonResponse,
    TeamRecommendationsRequest,
    TeamRecommendationsResponse,
)
from src.services.agent_service import AgentService

agent_route = APIRouter(prefix="/api", tags=["Agent"])


@agent_route.post(
    "/insights/{insight_id}/explain",
    response_model=GeneratedInsightExplanation,
)
async def explain_insight(
    insight_id: UUID,
    language: str = "en",
    audience: str = "general",
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.explain_match_insight(
        insight_id=insight_id,
        language=language,
        audience=audience,
    )


@agent_route.post(
    "/matches/{match_id}/agent/summary",
    response_model=MatchSummaryResponse,
)
async def summarize_match(
    match_id: UUID,
    data: AgentSummaryRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.generate_match_summary(
        match_id=match_id,
        language=data.language,
    )


@agent_route.post(
    "/matches/{match_id}/agent/ask",
    response_model=MatchQuestionResponse,
)
async def ask_about_match(
    match_id: UUID,
    data: MatchQuestionRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.answer_match_question(
        match_id=match_id,
        question=data.question,
        language=data.language,
    )


@agent_route.post(
    "/matches/{match_id}/agent/key-moments/explain",
    response_model=KeyMomentExplanation,
)
async def explain_key_moment(
    match_id: UUID,
    data: KeyMomentRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.explain_key_moment(
        match_id=match_id,
        event_id=data.event_id,
        language=data.language,
    )


@agent_route.post(
    "/matches/{match_id}/agent/tactical-analysis",
    response_model=TacticalAnalysisResponse,
)
async def generate_tactical_analysis(
    match_id: UUID,
    data: TacticalAnalysisRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.generate_tactical_analysis(
        match_id=match_id,
        team_id=data.team_id,
        language=data.language,
    )


@agent_route.post(
    "/matches/{match_id}/agent/team-comparison",
    response_model=TeamComparisonResponse,
)
async def compare_match_teams(
    match_id: UUID,
    data: AgentSummaryRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.compare_teams(
        match_id=match_id,
        language=data.language,
    )


@agent_route.post(
    "/matches/{match_id}/agent/player-analysis",
    response_model=PlayerAnalysisResponse,
)
async def analyze_player(
    match_id: UUID,
    data: PlayerAnalysisRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.generate_player_analysis(
        match_id=match_id,
        player_id=data.player_id,
        language=data.language,
    )


@agent_route.post(
    "/insights/{insight_id}/personalize",
    response_model=InsightPersonalizationResponse,
)
async def personalize_insight(
    insight_id: UUID,
    data: InsightPersonalizationRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.personalize_insight(
        insight_id=insight_id,
        audience=data.audience,
        language=data.language,
    )


@agent_route.post(
    "/matches/{match_id}/agent/recommendations",
    response_model=TeamRecommendationsResponse,
)
async def generate_team_recommendations(
    match_id: UUID,
    data: TeamRecommendationsRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return await agent_service.generate_recommendations(
        match_id=match_id,
        team_id=data.team_id,
        language=data.language,
    )
