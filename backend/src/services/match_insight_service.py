import hashlib
import json
import logging
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.agent_schema import GeneratedMatchInsights
from src.api.schemas.match_insight import MatchInsightCreate, MatchInsightResponse
from src.core.config import settings
from src.database.models.match import MatchStatus
from src.database.models.match_insights import MatchInsight, InsightType, Importance
from src.exceptions_handlers.bad_request_exception import BadRequestException
from src.exceptions_handlers.database_exception import DatabaseException
from src.exceptions_handlers.not_found_exception import NotFoundException
from src.repositories.match_insight_repository import MatchInsightRepository
from src.repositories.match_repository import MatchRepository
from src.services.agent_service import AgentService
from src.services.analytics_service import AnalyticsService
from .helper import Helper

logger = logging.getLogger(__name__)
GENERATION_VERSION = "1"


class MatchInsightService:
    def __init__(
        self,
        session: AsyncSession,
        analytic: AnalyticsService,
        agent_service: AgentService,
    ):
        self.session = session
        self.analytic = analytic
        self.agent_service = agent_service
        self.helper = Helper(self.session)
        self.match_repo = MatchRepository(self.session)
        self.match_insight_repo = MatchInsightRepository(self.session)

    @staticmethod
    def _generation_key(
        match_id: UUID,
        analytics: dict,
        language: str,
        audience: str,
    ) -> str:
        canonical_data = json.dumps(
            analytics,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical_data.encode("utf-8")).hexdigest()
        return hashlib.sha256(
            (
                f"{GENERATION_VERSION}:{match_id}:{language}:"
                f"{audience}:{digest}"
            ).encode("utf-8")
        ).hexdigest()

    async def generate_match_insights(
        self,
        match_id: UUID,
        language: str = "en",
        audience: str = "general",
    ) -> list[MatchInsightResponse]:
        match = await self.match_repo.get_for_update(match_id)
        if match is None:
            raise NotFoundException("Match not found")

        if match.status not in {MatchStatus.READY, MatchStatus.FINISHED}:
            await self.session.rollback()

            raise BadRequestException("Insights can only be generated for ready or finished matches")

        try:
            analytics = await self.analytic.run_match_analysis(match_id)
            generation_key = self._generation_key(
                match_id,
                analytics,
                language,
                audience,
            )
            existing = await self.match_insight_repo.get_by_generation_key(
                match_id,
                generation_key,
            )
            if existing:
                await self.session.commit()
                return [
                    MatchInsightResponse.model_validate(insight)
                    for insight in existing
                ]

            generated: GeneratedMatchInsights = (
                await self.agent_service.generate_match_insights(
                    match_id=match_id,
                    analytics=analytics,
                    language=language,
                    audience=audience,
                )
            )
            insights = [
                MatchInsight(
                    match_id=match_id,
                    insight_type=item.insight_type,
                    title=item.title,
                    content=item.content,
                    importance=item.importance,
                    minute=item.minute,
                    evidence={
                        **item.evidence.model_dump(mode="json"),
                        "generation_key": generation_key,
                    },
                    audience=audience,
                    language=language,
                    model_name=settings.GEMINI_MODEL,
                )
                for item in generated.insights
            ]
            await self.match_insight_repo.add_all(insights)
            await self.session.flush()
            for insight in insights:
                await self.session.refresh(insight)
            await self.session.commit()

            logger.info(
                "Generated and saved match insights",
                extra={"match_id": str(match_id), "count": len(insights)},
            )
            return [
                MatchInsightResponse.model_validate(insight)
                for insight in insights
            ]
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception(
                "Database error while generating match insights: match_id=%s",
                match_id,
            )
            raise DatabaseException("Failed to generate match insights") from exc
        except Exception:
            await self.session.rollback()
            raise

    async def create_insight(
        self,
        insight_data: MatchInsightCreate,
    ) -> MatchInsightResponse:
        await self.helper.get_match_or_404(insight_data.match_id)
        try:
            insight = MatchInsight(**insight_data.model_dump())
            self.session.add(insight)
            await self.session.flush()
            await self.session.refresh(insight)
            await self.session.commit()
            logger.info(
                "Match insight created: insight_id=%s, match_id=%s",
                insight.id,
                insight.match_id,
            )
            return MatchInsightResponse.model_validate(insight)
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception(
                "Database error while creating match insight: match_id=%s",
                insight_data.match_id,
            )
            raise DatabaseException("Failed to create match insight") from exc

    async def create_insights(
        self,
        insights_data: list[MatchInsightCreate],
    ) -> list[MatchInsightResponse]:
        if not insights_data:
            return []

        match_ids = {item.match_id for item in insights_data}
        if len(match_ids) != 1:
            raise BadRequestException("All insights must belong to the same match")

        match_id = next(iter(match_ids))
        await self.helper.get_match_or_404(match_id)
        try:
            insights = [
                MatchInsight(**item.model_dump())
                for item in insights_data
            ]
            self.session.add_all(insights)
            await self.session.flush()
            for insight in insights:
                await self.session.refresh(insight)
            await self.session.commit()
            logger.info(
                "Match insights created: match_id=%s, count=%s",
                match_id,
                len(insights),
            )
            return [
                MatchInsightResponse.model_validate(insight)
                for insight in insights
            ]
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception(
                "Database error while creating match insights: match_id=%s",
                match_id,
            )
            raise DatabaseException("Failed to create match insights") from exc

    async def get_insight_by_id(self, insight_id: UUID) -> MatchInsightResponse:
        insight = await self.helper.get_match_insight_or_404(insight_id)
        logger.info("Successful response of match insight: %s", insight_id)
        return MatchInsightResponse.model_validate(insight)

    async def get_match_insights(
        self,
        match_id: UUID,
        limit: int = 100,
        offset: int = 0,
        insight_type: InsightType | None = None,
        importance: Importance | None = None,
    ) -> list[MatchInsightResponse]:
        await self.helper.get_match_or_404(match_id)
        insights = await self.match_insight_repo.get_match_insights_by_match_id(
            match_id,
            limit,
            offset,
            insight_type,
            importance,
        )
        return [
            MatchInsightResponse.model_validate(insight)
            for insight in insights
        ]

    async def get_insights_by_type(
        self,
        match_id: UUID,
        insight_type: InsightType,
        offset: int = 0,
        limit: int = 100,
    ) -> list[MatchInsightResponse]:
        await self.helper.get_match_or_404(match_id)
        insights = await self.match_insight_repo.get_insights_by_type(
            match_id,
            insight_type,
            offset,
            limit,
        )
        return [
            MatchInsightResponse.model_validate(insight)
            for insight in insights
        ]

    async def get_insights_by_minute(
        self,
        match_id: UUID,
        start_minute: int,
        end_minute: int,
    ) -> list[MatchInsightResponse]:
        if start_minute < 0 or end_minute < start_minute:
            raise BadRequestException("Invalid minute range")
        await self.helper.get_match_or_404(match_id)
        insights = await self.match_insight_repo.get_match_with_start_end_munite(
            match_id,
            start_minute,
            end_minute,
        )
        return [
            MatchInsightResponse.model_validate(insight)
            for insight in insights
        ]
