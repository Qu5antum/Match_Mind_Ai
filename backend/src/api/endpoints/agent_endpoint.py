from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import get_agent_service
from src.api.schemas.agent_schema import (
    AgentSummaryRequest,
    GeneratedInsightExplanation,
    MatchQuestionRequest,
    MatchQuestionResponse,
    MatchSummaryResponse,
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
