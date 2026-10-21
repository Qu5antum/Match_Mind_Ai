from sqlalchemy import select
from uuid import UUID

from .base_repository import BaseRepository
from src.database.models.match_insights import MatchInsight, InsightType, Importance


class MatchInsightRepository(BaseRepository):
    model = MatchInsight

    async def get_match_insights_by_match_id(
        self, 
        match_id: UUID, 
        limit: int = 100, 
        offset: int = 0, 
        insight_type: InsightType | None = None,
        importance: Importance | None = None
    ) -> list[MatchInsight]:
        query = (
            select(self.model)
            .where(self.model.match_id == match_id)
        )

        if insight_type:
            query = query.where(self.model.insight_type == insight_type)

        if importance:
            query = query.where(self.model.importance == importance)

        result = await self.session.execute(
            query.order_by(self.model.minute.asc()).offset(offset).limit(limit)
        )

        return result.scalars().all()

    async def get_insights_by_type(
        self,
        match_id: UUID,
        insight_type: InsightType,
        offset: int = 0,
        limit: int = 100
    ) -> list[MatchInsight]:
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.match_id == match_id,
                self.model.insight_type == insight_type
            )
            .order_by(self.model.minute.asc())
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_match_with_start_end_munite(
            self, 
            match_id: UUID,
            start_minute: int, 
            end_minute: int
        ) -> list[MatchInsight]:
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.match_id == match_id,
                self.model.minute.between(start_minute, end_minute)
            )
        )

        return result.scalars().all()

    async def get_by_generation_key(
        self,
        match_id: UUID,
        generation_key: str,
    ) -> list[MatchInsight]:
        result = await self.session.execute(
            select(self.model)
            .where(
                self.model.match_id == match_id,
                self.model.evidence["generation_key"].as_string()
                == generation_key,
            )
            .order_by(self.model.minute.asc(), self.model.created_at.asc())
        )
        return result.scalars().all()
