from uuid import UUID
from sqlalchemy import select

from .base_repository import BaseRepository
from src.database.models.player import Player


class PlayerRepository(BaseRepository):
    model = Player

    async def get_players_by_team_id(self, team_id: UUID):
        result = await self.session.execute(
            select(self.model)
            .where(self.model.team_id == team_id)
        )

        return result.scalars().all()
