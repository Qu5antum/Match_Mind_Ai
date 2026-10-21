from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    short_name: str = Field(min_length=1, max_length=255)


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    short_name: str | None = Field(default=None, min_length=1, max_length=255)


class TeamResponse(BaseModel):
    id: UUID
    name: str
    short_name: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
