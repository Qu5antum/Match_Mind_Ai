from uuid import UUID
from sqlalchemy import select, func, delete

from .base_repository import BaseRepository
from src.database.models.match_events import MatchEvent, EventType


class MatchEventRepository(BaseRepository):
    model = MatchEvent

    async def get_match_events_with_pagination(
        self,
        match_id: UUID,
        offset: int = 0,
        limit: int = 100,
        event_type: EventType | None = None,
        team_id: UUID | None = None,
        player_id: UUID | None = None,
        after_sequence: int | None = None,
    ) -> list[MatchEvent]:
        query = (select(self.model).where(self.model.match_id == match_id))

        if event_type:
            query = query.where(self.model.event_type == event_type)

        if after_sequence is not None:
            query = query.where(self.model.sequence > after_sequence)

        if team_id is not None:
            query = query.where(self.model.team_id == team_id)

        if player_id is not None:
            query = query.where(self.model.player_id == player_id)

        query = query.order_by(self.model.sequence.asc()).offset(offset).limit(limit)

        result = await self.session.execute(query)

        return result.scalars().all()

    async def get_match_events_with_sequence(
        self, 
        match_id: UUID, 
        sequence: int, 
        limit: int = 100, 
        offset = 0
    ) -> list[MatchEvent]:
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.match_id == match_id,
                self.model.sequence == sequence
            )
            .order_by(self.model.sequence.asc())
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_match_by_event_type(
            self, 
            match_id: UUID,
            event_type: EventType,
            offset: int = 0,
            limit: int = 100
        ) -> list[MatchEvent]:
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.event_type == event_type,
                self.model.match_id == match_id
            )
            .order_by(self.model.sequence.asc())
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_match_events_by_player_id(
        self, 
        match_id: UUID,
        player_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> list[MatchEvent]:
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.player_id == player_id,
                self.model.match_id == match_id
            )
            .order_by(self.model.sequence.asc())
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_match_events_count(
        self, 
        match_id: UUID, 
        event_type: EventType | None = None,
        team_id: UUID | None = None,
        player_id: UUID | None = None
    ):
        query = (
            select(func.count(self.model))
            .where(self.model.match_id == match_id)
        )

        if event_type:
            query = query.where(self.model.event_type == event_type)

        if team_id:
            query = query.where(self.model.team_id == team_id)

        if player_id:
            query = query.where(self.model.player_id == player_id)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def delete_events_by_match_id(self, match_id: UUID) -> int:
        query = delete(self.model).where(
            self.model.match_id == match_id
        )

        result = await self.session.execute(query)
        return result.rowcount or 0
