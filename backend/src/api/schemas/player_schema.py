from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime


class CreatePlayer(BaseModel):
    name: str
    position: str
    team_id: UUID
    passing: int = Field(..., ge=1, le=100, description="Value must be from 1 to 100")
    shooting: int = Field(..., ge=1, le=100, description="Value must be from 1 to 100")
    dribbling: int = Field(..., ge=1, le=100, description="Value must be from 1 to 100")
    defending: int = Field(..., ge=1, le=100, description="Value must be from 1 to 100")
    pace: int = Field(..., ge=1, le=100, description="Value must be from 1 to 100")
    stamina: int = Field(..., ge=1, le=100, description="Value must be from 1 to 100")
    vision: int = Field(..., ge=1, le=100, description="Value must be from 1 to 100")


class UpdatePlayer(BaseModel):
    name: str | None = None
    position: str | None = None
    team_id: UUID | None = None
    passing: int | None = Field(None, ge=1, le=100, description="Value must be from 1 to 100")
    shooting: int | None = Field(None, ge=1, le=100, description="Value must be from 1 to 100")
    dribbling: int | None = Field(None, ge=1, le=100, description="Value must be from 1 to 100")
    defending: int | None = Field(None, ge=1, le=100, description="Value must be from 1 to 100")
    pace: int | None = Field(None, ge=1, le=100, description="Value must be from 1 to 100")
    stamina: int | None = Field(None, ge=1, le=100, description="Value must be from 1 to 100")
    vision: int | None = Field(None, ge=1, le=100, description="Value must be from 1 to 100")


class PlayerResponse(BaseModel):
    id: UUID
    name: str
    position: str
    team_id: UUID
    passing: int
    shooting: int 
    dribbling: int 
    defending: int 
    pace: int 
    stamina: int 
    vision: int 
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class BulkCreatePlayers(BaseModel):
    players: list[CreatePlayer] = Field(min_length=1, max_length=30)
