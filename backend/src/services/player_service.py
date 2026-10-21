import logging
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID

from src.database.db import AsyncSession
from src.api.schemas.player_schema import CreatePlayer, PlayerResponse, UpdatePlayer, BulkCreatePlayers
from src.repositories.player_repository import PlayerRepository
from .helper import Helper
from src.exceptions_handlers.database_exception import DatabaseException

logger = logging.getLogger(__name__)


class PlayerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.helper = Helper(session=self.session)
        self.player_repo = PlayerRepository(session=self.session)

    async def create_player(self, data: CreatePlayer) -> PlayerResponse:
        await self.helper.get_team_or_404(data.team_id)
        try:
            new_player = await self.player_repo.create(
                name=data.name,
                position=data.position,
                team_id=data.team_id,
                passing=data.passing,
                shooting=data.shooting,
                dribbling=data.dribbling,
                defending=data.defending,
                pace=data.pace,
                stamina=data.stamina,
                vision=data.vision
            )

            await self.session.commit()
            await self.session.refresh(new_player)

            logger.info(f"Player successfully created: {new_player.id}")

            return new_player

        except SQLAlchemyError as e:
            await self.session.rollback()
        
            logger.error(
                f"Database error, player not created: {e}",
                exc_info=True
            )

            raise DatabaseException("Database error, player not created")

    async def update_player(self, player_id: UUID, data: UpdatePlayer) -> PlayerResponse:
        player = await self.helper.get_player_or_404(player_id=player_id)
        updates = data.model_dump(exclude_unset=True, exclude_none=True)
        if "team_id" in updates:
            await self.helper.get_team_or_404(updates["team_id"])

        try:
            updated_player = await self.player_repo.update(
                obj=player,
                data=updates
            )

            await self.session.commit()
            await self.session.refresh(updated_player)

            logger.info(f"Player successfully updated: {player_id}")

            return updated_player

        except SQLAlchemyError as e:
            await self.session.rollback()
        
            logger.error(
                f"Database error, player not updated: {e}",
                exc_info=True
            )

            raise DatabaseException("Database error, player not updated")

    async def get_player(self, player_id: UUID) -> PlayerResponse:
        player = await self.helper.get_player_or_404(player_id)
        return PlayerResponse.model_validate(player)

    async def delete_player(self, player_id: UUID) -> None:
        await self.helper.get_player_or_404(player_id)
        try:
            await self.player_repo.delete(player_id)
            await self.session.commit()
        except SQLAlchemyError as exc:
            await self.session.rollback()
            logger.exception("Database error while deleting player %s", player_id)
            raise DatabaseException("Database error, player not deleted") from exc

    async def create_many_player(self, data: BulkCreatePlayers) -> str:
        try:
            db_players = [
                self.player_repo.model(**player.model_dump()) 
                for player in data.players
            ]
            
            await self.player_repo.add_all(db_players)

            await self.session.commit()

            logger.info("Players successfully created")

            return "Players successfully created"

        except SQLAlchemyError as e:
            await self.session.rollback()
        
            logger.error(
                f"Database error, players not created: {e}",
                exc_info=True
            )

            raise DatabaseException("Database error, players not created")

    async def get_player_by_team_id(self, team_id: UUID) -> list[PlayerResponse]:
        await self.helper.get_team_or_404(team_id=team_id)

        players = await self.player_repo.get_players_by_team_id(team_id=team_id)

        logger.info(f"Successfull response of player by team ID: {team_id}")

        return players
