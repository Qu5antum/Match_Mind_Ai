from sqlalchemy import exists, or_
from uuid import UUID

from .base_repository import BaseRepository
from src.database.models.team import Team


class TeamRepository(BaseRepository):
    model = Team

    async def is_team_with_name_or_short_name_exists(self, name: str, short_name: str) -> bool:
        stmt = exists().where(
            or_(
                self.model.name == name,
                self.model.short_name == short_name
            )
        ).select()
        
        return await self.session.scalar(stmt)

    async def has_duplicate_name(
        self,
        name: str,
        short_name: str,
        exclude_id: UUID | None = None,
    ) -> bool:
        conditions = [
            self.model.name == name,
            self.model.short_name == short_name,
        ]
        stmt = exists().where(or_(*conditions))
        if exclude_id is not None:
            stmt = exists().where(
                or_(*conditions),
                self.model.id != exclude_id,
            )
        return bool(await self.session.scalar(stmt.select()))
