from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from .base_repository import BaseRepository
from src.database.models.match import Match
from src.database.models.match_teams import MatchTeam
from src.database.models.team import Team


class MatchRepository(BaseRepository):
    model = Match

    async def get_for_update(self, match_id: UUID) -> Match | None:
        result = await self.session.execute(
            select(self.model)
            .where(self.model.id == match_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_match_details(self, match_id: UUID) -> Match:
        result = await self.session.execute(
            select(self.model)
            .options(selectinload(self.model.match_teams))
            .options(selectinload(self.model.match_events))
            .options(selectinload(self.model.match_insights))
            .where(self.model.id == match_id)
        )

        return result.scalar_one_or_none()

    async def load_match_with_match_teams_players(self, match_id: UUID):
        result = await self.session.execute(
            select(self.model)
            .where(self.model.id == match_id)
            .options(
                selectinload(Match.match_teams)
                .selectinload(MatchTeam.team)
                .selectinload(Team.players)
            )
        )

        return result.scalar_one_or_none()
