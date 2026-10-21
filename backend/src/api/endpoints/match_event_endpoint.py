from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_match_event_service
from src.api.schemas.match_schema import MatchEventCreate, MatchEventResponse
from src.database.models.match_events import EventType
from src.services.match_event_service import MatchEventService

match_event_route = APIRouter(prefix="/api/matches", tags=["Match events"])


@match_event_route.post(
    "/{match_id}/events",
    response_model=MatchEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_match_event(
    match_id: UUID,
    data: MatchEventCreate,
    event_service: MatchEventService = Depends(get_match_event_service),
):
    return await event_service.create_match_event(
        {"match_id": match_id, **data.model_dump()}
    )


@match_event_route.post(
    "/{match_id}/events/bulk",
    response_model=list[MatchEventResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_match_events(
    match_id: UUID,
    events: list[MatchEventCreate],
    event_service: MatchEventService = Depends(get_match_event_service),
):
    return await event_service.create_events(
        [
            {"match_id": match_id, **event.model_dump()}
            for event in events
        ]
    )


@match_event_route.get("/{match_id}/events/count")
async def get_match_event_count(
    match_id: UUID,
    event_type: EventType | None = None,
    team_id: UUID | None = None,
    player_id: UUID | None = None,
    event_service: MatchEventService = Depends(get_match_event_service),
):
    count = await event_service.get_events_count(
        match_id=match_id,
        event_type=event_type,
        team_id=team_id,
        player_id=player_id,
    )
    return {"count": count}


@match_event_route.delete("/{match_id}/events")
async def delete_match_events(
    match_id: UUID,
    event_service: MatchEventService = Depends(get_match_event_service),
):
    deleted_count = await event_service.delete_match_events(match_id)
    return {"deleted_count": deleted_count}


@match_event_route.get("/{match_id}/events")
@match_event_route.get("/{match_id}/timeline")
async def get_match_events(
    match_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    event_type: EventType | None = None,
    team_id: UUID | None = None,
    player_id: UUID | None = None,
    after_sequence: int | None = Query(default=None, ge=0),
    event_service: MatchEventService = Depends(get_match_event_service),
):
    return await event_service.get_match_events(
        match_id=match_id,
        offset=offset,
        limit=limit,
        event_type=event_type,
        team_id=team_id,
        player_id=player_id,
        after_sequence=after_sequence,
    )


@match_event_route.get("/{match_id}/events/by-type/{event_type}")
async def get_match_events_by_type(
    match_id: UUID,
    event_type: EventType,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    event_service: MatchEventService = Depends(get_match_event_service),
):
    return await event_service.get_match_events_by_type(
        match_id=match_id,
        event_type=event_type,
        offset=offset,
        limit=limit,
    )


@match_event_route.get("/{match_id}/events/by-player/{player_id}")
async def get_player_match_events(
    match_id: UUID,
    player_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    event_service: MatchEventService = Depends(get_match_event_service),
):
    return await event_service.get_players_events(
        match_id=match_id,
        player_id=player_id,
        offset=offset,
        limit=limit,
    )


@match_event_route.get("/{match_id}/events/after/{sequence}")
async def get_events_after_sequence(
    match_id: UUID,
    sequence: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    event_service: MatchEventService = Depends(get_match_event_service),
):
    return await event_service.get_match_events_after_sequence(
        match_id=match_id,
        sequence=sequence,
        limit=limit,
        offset=offset,
    )


@match_event_route.get("/events/{event_id}", response_model=MatchEventResponse)
async def get_match_event(
    event_id: UUID,
    event_service: MatchEventService = Depends(get_match_event_service),
):
    return await event_service.get_event_by_id(event_id)
