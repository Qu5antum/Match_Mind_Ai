from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from src.database.db import AsyncSession, get_session
from src.services.team_service import TeamService
from src.api.schemas.team_schema import TeamCreate, TeamResponse, TeamUpdate


team_route = APIRouter(
    prefix="/api",
    tags=["Team"]
)

async def get_team_service(session: AsyncSession = Depends(get_session)):
    return TeamService(session=session)


@team_route.post("/team", response_model=TeamResponse, status_code=201)
async def create_team(
    data: TeamCreate,
    team_service: TeamService = Depends(get_team_service)
):
    return await team_service.create_team(data=data)


@team_route.get("/team", response_model=list[TeamResponse], status_code=200)
async def get_teams(
    limit: int = 20,
    offset: int = 0,
    team_service: TeamService = Depends(get_team_service)
):
    return await team_service.get_all_teams(limit=limit, offset=offset)


@team_route.get("/team/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: UUID,
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.get_team(team_id)


@team_route.patch("/team/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: UUID,
    data: TeamUpdate,
    team_service: TeamService = Depends(get_team_service),
):
    return await team_service.update_team(team_id, data)


@team_route.delete("/team/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    team_service: TeamService = Depends(get_team_service),
):
    await team_service.delete_team(team_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)