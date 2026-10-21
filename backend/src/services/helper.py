import logging
from uuid import UUID
from typing import Optional

from src.database.db import AsyncSession
from src.database.models.match import Match
from src.database.models.team import Team
from src.database.models.player import Player
from src.database.models.match_events import MatchEvent
from src.database.models.match_insights import MatchInsight
from src.repositories.match_repository import MatchRepository
from src.repositories.team_repository import TeamRepository
from src.repositories.player_repository import PlayerRepository
from src.repositories.match_event_repository import MatchEventRepository
from src.repositories.match_insight_repository import MatchInsightRepository

from src.exceptions_handlers.not_found_exception import NotFoundException

logger = logging.getLogger(__name__)


class Helper:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.match_repo = MatchRepository(self.session)
        self.team_repo = TeamRepository(self.session)
        self.player_repo = PlayerRepository(self.session)
        self.match_event_repo = MatchEventRepository(self.session)
        self.match_insight_repo = MatchInsightRepository(self.session)

    async def get_match_or_404(self, match_id: UUID) -> Optional[Match]:
        match = await self.match_repo.get(id=match_id)

        if not match:
            logger.warning(f"Match not found: {match_id}")

            raise NotFoundException("Match not found")

        return match

    async def get_team_or_404(self, team_id: UUID) -> Optional[Team]:
        team = await self.team_repo.get(id=team_id)

        if not team:
            logger.warning(f"Team not found: {team_id}")
            
            raise NotFoundException("Team not found")

        return team

    async def get_player_or_404(self, player_id: UUID) -> Optional[Player]:
        player = await self.player_repo.get(id=player_id)

        if not player:
            logger.warning(f"Player not found: {player_id}")

            raise NotFoundException("Player not found")

        return player

    async def get_match_event_or_404(self, match_event_id: UUID) -> Optional[MatchEvent]:
        event = await self.match_event_repo.get(id=match_event_id)

        if not event:
            logger.warning(f"Event not found: {match_event_id}")

            raise NotFoundException("Event not found")

        return event

    async def get_match_insight_or_404(self, match_insight_id: UUID) -> Optional[MatchInsight]:
        insight = await self.match_insight_repo.get(id=match_insight_id)

        if not insight:
            logger.warning(f"Match insight not found: {match_insight_id}")

            raise NotFoundException("Match insight not found")

        return insight
