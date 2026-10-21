import logging
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError

from src.database.db import AsyncSession
from src.repositories.team_repository import TeamRepository
from src.api.schemas.team_schema import TeamCreate, TeamResponse
from src.exceptions_handlers.bad_request_exception import BadRequestException
from src.exceptions_handlers.database_exception import DatabaseException
from src.exceptions_handlers.not_found_exception import NotFoundException
from src.api.schemas.team_schema import TeamUpdate

logger = logging.getLogger(__name__)


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repo = TeamRepository(session=self.session)

    async def create_team(self, data: TeamCreate) -> TeamResponse:
        is_name_or_short_name_exists = await self.team_repo.is_team_with_name_or_short_name_exists(
            name=data.name, 
            short_name=data.short_name
        )

        if is_name_or_short_name_exists:
            logger.warning(f"Team with this name or short name is exists: {data.name}")

            raise BadRequestException("Team with name already exists")

        try:
            new_team = await self.team_repo.create(
                name=data.name,
                short_name=data.short_name
            )

            await self.session.commit()
            await self.session.refresh(new_team)

            logger.info(f"New team successfully created: {new_team.id}")

            return new_team

        except SQLAlchemyError as e:
            await self.session.rollback()
        
            logger.error(
                f"Database error, team not created: {e}",
                exc_info=True
            )

            raise DatabaseException("Database error, team not created")

    async def get_all_teams(self, limit: int = 20, offset: int = 0):
        teams = await self.team_repo.get_all(limit=limit, offset=offset)

        logger.info("Successfull response of teams")

        return teams

    async def get_team(self, team_id: UUID):
        team = await self.team_repo.get(id=team_id)
        if team is None:
            raise NotFoundException("Team not found")
        return team

    async def update_team(self, team_id: UUID, data: TeamUpdate) -> TeamResponse:
        team = await self.get_team(team_id)
        updates = data.model_dump(exclude_unset=True, exclude_none=True)
        if not updates:
            return team

        if await self.team_repo.has_duplicate_name(
            name=updates.get("name", team.name),
            short_name=updates.get("short_name", team.short_name),
            exclude_id=team_id,
        ):
            raise BadRequestException("Team name or short name already exists")

        try:
            await self.team_repo.update(obj=team, data=updates)
            await self.session.commit()
            await self.session.refresh(team)
            return team
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception("Database error while updating team %s", team_id)
            raise DatabaseException("Database error, team not updated") from exc

    async def delete_team(self, team_id: UUID) -> None:
        await self.get_team(team_id)
        try:
            await self.team_repo.delete(team_id)
            await self.session.commit()
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception("Database error while deleting team %s", team_id)
            raise DatabaseException("Database error, team not deleted") from exc
