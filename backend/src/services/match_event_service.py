import logging
from typing import Any
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID

from src.database.db import AsyncSession
from src.database.models.match_events import MatchEvent, EventType
from src.repositories.match_repository import MatchRepository
from src.repositories.match_event_repository import MatchEventRepository
from .helper import Helper
from src.api.schemas.match_schema import MatchEventResponse
from src.exceptions_handlers.database_exception import DatabaseException
from src.exceptions_handlers.not_found_exception import NotFoundException
from src.exceptions_handlers.business_logic_exception import BusinessLogicException

logger = logging.getLogger(__name__)


class MatchEventService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.match_repo = MatchRepository(self.session)
        self.match_event_repo = MatchEventRepository(self.session)
        self.helper = Helper(self.session)

    async def create_match_event(self, event_data: dict[str, Any]) -> MatchEventResponse:
        await self.helper.get_match_or_404(event_data["match_id"])

        try:
            new_match_event = MatchEvent(**event_data)
            self.session.add(new_match_event)
            await self.session.commit()
            await self.session.refresh(new_match_event)

            logger.info(f"New match events successfully created: {new_match_event.id}")

            return new_match_event

        except SQLAlchemyError as e:
            await self.session.rollback()

            logger.error(
                f"Database error, match event not created: {e}",
                exc_info=True
            )

            raise DatabaseException("Database error, match event not created") from e

    async def create_events(
        self,
        events_data: list[dict[str, Any]],
    ) -> list[MatchEventResponse]:
        if not events_data:
            return []

        try:
            match_ids = {event.get("match_id") for event in events_data}

            if None in match_ids:
                raise BusinessLogicException(
                    "Every event must contain match_id"
                )

            if len(match_ids) != 1:
                raise BusinessLogicException(
                    "All events in a batch must belong to one match"
                )

            match_id = next(iter(match_ids))
            await self.helper.get_match_or_404(match_id)

            sequences = [event.get("sequence") for event in events_data]

            if None in sequences:
                raise BusinessLogicException(
                    "Every event must contain sequence"
                )

            if len(sequences) != len(set(sequences)):
                raise BusinessLogicException(
                    "Duplicate sequence numbers in event batch"
                )

            data = [
                MatchEvent(**event)
                for event in events_data
            ]

            for event in events_data:
                logger.debug(
                    "Saving match event",
                    extra={
                        "event_type": str(event.get("event_type")),
                        "event_type_repr": repr(event.get("event_type")),
                    },
                )

            self.session.add_all(data)
            await self.session.commit()

            logger.info(
                "Match events successfully saved",
                extra={
                    "match_id": str(match_id),
                    "event_count": len(data),
                },
            )

            return data

        except (NotFoundException, BusinessLogicException):
            raise

        except SQLAlchemyError as exc:
            await self.session.rollback()

            logger.exception("Database error while creating match events")

            raise DatabaseException("Database error while creating match events") from exc

    async def get_event_by_id(self, event_id: UUID) -> MatchEventResponse:
        event = await self.helper.get_match_event_or_404(event_id)

        logger.info(f"Successfull response of event: {event_id}")

        return event

    async def get_match_events(
        self,
        match_id: UUID,
        offset: int = 0,
        limit: int = 100,
        event_type: EventType | None = None,
        team_id: UUID | None = None,
        player_id: UUID | None = None,
        after_sequence: int | None = None,
    ) -> list[MatchEventResponse]:
        if offset < 0:
            raise BusinessLogicException("Offset cannot be negative")

        if not 1 <= limit <= 500:
            raise BusinessLogicException(
                "Limit must be between 1 and 500"
            )

        if after_sequence is not None and after_sequence < 0:
            raise BusinessLogicException(
                "Sequence cannot be negative"
            )

        await self.helper.get_match_or_404(match_id)

        if team_id is not None:
            await self.helper.get_team_or_404(team_id)

        if player_id is not None:
            await self.helper.get_player_or_404(player_id)

        return await self.match_event_repo.get_match_events_with_pagination(
            match_id=match_id,
            offset=offset,
            limit=limit,
            event_type=event_type,
            team_id=team_id,
            player_id=player_id,
            after_sequence=after_sequence,
        )

    async def get_match_events_after_sequence(
        self, 
        match_id: UUID,
        sequence: int,
        limit: int = 100,
        offset: int = 0
    ) -> list[MatchEventResponse]:
        if sequence is not None and sequence < 0:
            raise BusinessLogicException("Sequence cannot be negative")

        await self.helper.get_match_or_404(match_id)

        events = await self.match_event_repo.get_match_events_with_sequence(
            match_id=match_id,
            sequence=sequence,
            limit=limit,
            offset=offset
        )

        logger.info(f"Successfull response of events: {match_id}")

        return events

    async def get_match_events_after_suquence(
        self,
        match_id: UUID,
        sequence: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MatchEventResponse]:
        return await self.get_match_events_after_sequence(
            match_id=match_id,
            sequence=sequence,
            limit=limit,
            offset=offset,
        )

    async def get_match_events_by_type(
        self, 
        match_id: UUID,
        event_type: EventType,
        offset: int = 0,
        limit: int = 100
    ) -> list[MatchEventResponse]:
        await self.helper.get_match_or_404(match_id)

        events = await self.match_event_repo.get_match_by_event_type(
            match_id=match_id,
            event_type=event_type,
            offset=offset,
            limit=limit
        )

        logger.info(f"Successfull response of events by status: {event_type}")

        return events

    async def get_players_events(
        self,
        match_id: UUID,
        player_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> list[MatchEventResponse]:
        if player_id:
            await self.helper.get_player_or_404(player_id)
        
        await self.helper.get_match_or_404(match_id)

        events = await self.match_event_repo.get_match_events_by_player_id(
            match_id=match_id,
            player_id=player_id,
            offset=offset,
            limit=limit
        )

        logger.info(f"Successfull response of events by player id: {player_id}")

        return events

    async def get_events_count(
        self, 
        match_id: UUID,
        event_type: EventType | None = None,
        team_id: UUID | None = None,
        player_id: UUID | None = None
    ) -> int:
        await self.helper.get_match_or_404(match_id)

        if player_id:
            await self.helper.get_player_or_404(player_id)

        if team_id:
            await self.helper.get_team_or_404(team_id)
        
        events_count = await self.match_event_repo.get_match_events_count(
            match_id=match_id,
            event_type=event_type,
            team_id=team_id,
            player_id=player_id
        )

        logger.info(f"Successfull response count of events: {match_id}")

        return events_count

    async def delete_match_events(self, match_id: UUID) -> int:
        await self.helper.get_match_or_404(match_id)

        try:
            deleted_row_count = (
                await self.match_event_repo.delete_events_by_match_id(
                    match_id
                )
            )

            await self.session.commit()

            logger.info(
                "Match events deleted",
                extra={
                    "match_id": str(match_id),
                    "deleted_count": deleted_row_count,
                },
            )

            return deleted_row_count

        except SQLAlchemyError as exc:
            await self.session.rollback()

            logger.exception("Failed to delete match events")

            raise DatabaseException("Database error while deleting match events") from exc
