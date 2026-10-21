from fastapi import APIRouter, Depends, Response, status
from uuid import UUID

from src.database.db import AsyncSession, get_session
from src.services.player_service import PlayerService
from src.api.schemas.player_schema import (
    BulkCreatePlayers,
    CreatePlayer,
    PlayerResponse,
    UpdatePlayer,
)


player_route = APIRouter(
    prefix="/api",
    tags=["Player"]
)


async def get_player_service(session: AsyncSession = Depends(get_session)):
    return PlayerService(session=session)


@player_route.post("/player/bulk", status_code=201)
async def create_many_player(
    data: BulkCreatePlayers,
    player_service: PlayerService = Depends(get_player_service)
):
    return await player_service.create_many_player(data=data)


@player_route.post("/player", response_model=PlayerResponse, status_code=201)
async def create_player(
    data: CreatePlayer,
    player_service: PlayerService = Depends(get_player_service),
):
    return await player_service.create_player(data=data)


@player_route.get("/player/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: UUID,
    player_service: PlayerService = Depends(get_player_service),
):
    return await player_service.get_player(player_id)


@player_route.patch("/player/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: UUID,
    data: UpdatePlayer,
    player_service: PlayerService = Depends(get_player_service),
):
    return await player_service.update_player(player_id, data)


@player_route.delete("/player/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: UUID,
    player_service: PlayerService = Depends(get_player_service),
):
    await player_service.delete_player(player_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@player_route.get("/team/{team_id}/players", response_model=list[PlayerResponse], status_code=200)
async def get_players_by_team(
    team_id: UUID,
    player_service: PlayerService = Depends(get_player_service)
):
    return await player_service.get_player_by_team_id(team_id=team_id)
