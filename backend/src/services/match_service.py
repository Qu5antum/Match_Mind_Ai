import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from uuid import UUID

from src.database.db import AsyncSession
from src.database.models.match import MatchStatus
from src.api.schemas.match_schema import CreateMatch, MatchResponse, DetailedMatchResponse
from src.repositories.match_repository import MatchRepository
from src.repositories.match_team_repository import MatchTeamRepository
from .helper import Helper
from src.exceptions_handlers.database_exception import DatabaseException
from src.exceptions_handlers.not_found_exception import NotFoundException
from src.exceptions_handlers.business_logic_exception import BusinessLogicException

logger = logging.getLogger(__name__)


class MatchService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.helper = Helper(session=self.session)
        self.match_repo = MatchRepository(session=self.session)
        self.match_team_repo = MatchTeamRepository(session=self.session)

    async def create_match(self, data: CreateMatch) -> MatchResponse:
        if data.home_team_id == data.away_team_id:
            raise BusinessLogicException("Home team and away team must be different")

        await self.helper.get_team_or_404(team_id=data.home_team_id)
        await self.helper.get_team_or_404(team_id=data.away_team_id)

        try:
            new_match = await self.match_repo.create(
                home_team_id=data.home_team_id,
                away_team_id=data.away_team_id,
                seed=data.seed,
                scenario=data.scenario.model_dump(mode="json"),
            )

            await self.match_repo.session.flush()

            await self.match_team_repo.create(
                match_id=new_match.id,
                team_id=data.home_team_id,
                side="home",
                formation=data.scenario.home_formation,
                tactics={},
                lineup={}
            )
            await self.match_team_repo.create(
                match_id=new_match.id,
                team_id=data.away_team_id,
                side="away",
                formation=data.scenario.away_formation,
                tactics={},
                lineup={}
            )

            await self.session.commit()
            await self.session.refresh(new_match)

            logger.info(
                "Match created successfully",
                extra={"match_id": str(new_match.id)}
            )

            return new_match

        except SQLAlchemyError as e:
            await self.session.rollback()
        
            logger.error(
                f"Database error, match not created: {e}",
                exc_info=True
            )

            raise DatabaseException("Database error, match not created") from e

    async def _change_status(self, match_id: UUID, new_status: MatchStatus) -> str:
        match = await self.helper.get_match_or_404(match_id=match_id)

        current_status = MatchStatus(match.status)

        if not current_status.can_transition_to(new_status):
            logger.warning(
                f"Invalid status transition from {current_status} to {new_status}",
                extra={"match_id": str(match_id), "current_status": current_status, "new_status": new_status}
            )

            raise BusinessLogicException(f"Transition from {current_status} to {new_status} is not allowed")

        try:
            match.status = new_status
            await self.session.flush()
            await self.session.commit()

            logger.info(f"Match status successfully updated to {new_status}: {match.id}")
            return "Match status successfully updated"

        except (IntegrityError, SQLAlchemyError) as e:
            await self.session.rollback()
            logger.error(
                f"Database error, match status not updated: {e}",
                exc_info=True
            )
            raise DatabaseException("Database error, match not updated") from e

    async def start_simulation(self, match_id: UUID) -> str:
        return await self._change_status(match_id, MatchStatus.SIMULATING)
    
    async def set_ready(self, match_id: UUID) -> str:
        return await self._change_status(match_id, MatchStatus.READY)

    async def start_playback(self, match_id: UUID) -> str:
        return await self._change_status(match_id, MatchStatus.PLAYING)

    async def pause_match(self, match_id: UUID) -> str:
        return await self._change_status(match_id, MatchStatus.PAUSED)

    async def finish_match(self, match_id: UUID) -> str:
        return await self._change_status(match_id, MatchStatus.FINISHED)

    async def fail_match(self, match_id: UUID) -> str:
        return await self._change_status(match_id, MatchStatus.FAILED)

    async def get_matches(self, limit: int = 20, offset: int = 0) -> list[MatchResponse]:
        matches = await self.match_repo.get_all(limit=limit, offset=offset)

        logger.info("Successfull response of matches")

        return matches

    async def get_match_by_id(self, match_id: UUID) -> MatchResponse:
        match = await self.helper.get_match_or_404(match_id=match_id)

        logger.info(f"Successfull response of match: {match_id}")

        return match

    async def get_match_detail(self, match_id: UUID) -> DetailedMatchResponse:
        match = await self.match_repo.get_match_details(match_id=match_id)
        
        if not match:
            logger.warning(f"Match not found by id: {match_id}")

            raise NotFoundException("Match not found")

        logger.info(f"Successfull response of match: {match_id}")

        return match
