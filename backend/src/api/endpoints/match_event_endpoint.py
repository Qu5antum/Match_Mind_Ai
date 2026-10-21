from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_match_event_service
from src.database.models.match_events import EventType
from src.services.match_event_service import MatchEventService

match_event_route = APIRouter(prefix="/api/matches", tags=["Match events"])


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
