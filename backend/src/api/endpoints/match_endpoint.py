from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_match_service, get_simulator_service
from src.api.schemas.match_schema import CreateMatch, DetailedMatchResponse, MatchResponse
from src.services.match_service import MatchService
from src.services.simulator_service import SimulatorService

match_route = APIRouter(prefix="/api/matches", tags=["Match"])


@match_route.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    data: CreateMatch,
    match_service: MatchService = Depends(get_match_service),
):
    return await match_service.create_match(data)


@match_route.get("", response_model=list[MatchResponse])
async def get_matches(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    match_service: MatchService = Depends(get_match_service),
):
    return await match_service.get_matches(limit, offset)


@match_route.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: UUID,
    match_service: MatchService = Depends(get_match_service),
):
    return await match_service.get_match_by_id(match_id)


@match_route.get("/{match_id}/detail", response_model=DetailedMatchResponse)
async def get_match_detail(
    match_id: UUID,
    match_service: MatchService = Depends(get_match_service),
):
    return await match_service.get_match_detail(match_id)


@match_route.post("/{match_id}/simulate", response_model=MatchResponse)
async def simulate_match(
    match_id: UUID,
    simulator_service: SimulatorService = Depends(get_simulator_service),
    match_service: MatchService = Depends(get_match_service),
):
    await simulator_service.simulate_match(match_id)
    return await match_service.get_match_by_id(match_id)


@match_route.post("/{match_id}/play")
async def play_match(
    match_id: UUID,
    match_service: MatchService = Depends(get_match_service),
):
    return {"message": await match_service.start_playback(match_id)}


@match_route.post("/{match_id}/pause")
async def pause_match(
    match_id: UUID,
    match_service: MatchService = Depends(get_match_service),
):
    return {"message": await match_service.pause_match(match_id)}


@match_route.post("/{match_id}/finish")
async def finish_match(
    match_id: UUID,
    match_service: MatchService = Depends(get_match_service),
):
    return {"message": await match_service.finish_match(match_id)}
