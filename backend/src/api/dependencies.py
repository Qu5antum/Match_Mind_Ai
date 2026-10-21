from fastapi import Depends

from src.database.db import AsyncSession, get_session
from src.providers.gemini_provider import GeminiProvider
from src.providers.manus_provider import ManusProvider
from src.services.agent_service import AgentService
from src.services.analytics_service import AnalyticsService
from src.services.match_event_service import MatchEventService
from src.services.match_insight_service import MatchInsightService
from src.services.match_service import MatchService
from src.services.simulator_service import SimulatorService


async def get_match_service(
    session: AsyncSession = Depends(get_session),
) -> MatchService:
    return MatchService(session=session)


async def get_match_event_service(
    session: AsyncSession = Depends(get_session),
) -> MatchEventService:
    return MatchEventService(session=session)


async def get_analytics_service(
    session: AsyncSession = Depends(get_session),
    match_event_service: MatchEventService = Depends(get_match_event_service),
) -> AnalyticsService:
    return AnalyticsService(
        session=session,
        match_event_service=match_event_service
    )


async def get_agent_service(
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> AgentService:
    return AgentService(
        session=session,
        analytic_service=analytics_service,
        provider=GeminiProvider()
    )


async def get_match_insight_service(
    session: AsyncSession = Depends(get_session),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    agent_service: AgentService = Depends(get_agent_service),
) -> MatchInsightService:
    return MatchInsightService(
        session=session,
        analytic=analytics_service,
        agent_service=agent_service
    )


async def get_simulator_service(
    session: AsyncSession = Depends(get_session),
    match_service: MatchService = Depends(get_match_service),
    match_event_service: MatchEventService = Depends(get_match_event_service),
) -> SimulatorService:
    return SimulatorService(
        session=session,
        match_service=match_service,
        match_event_service=match_event_service
    )
