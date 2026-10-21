from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Literal
from uuid import UUID
from datetime import datetime

from src.database.models.match import MatchStatus
from src.database.models.match_events import EventType
from .match_insight import MatchInsightResponse


class MatchScenario(BaseModel):
    duration_minutes: Literal[90, 120] = 90
    difficulty: Literal["easy", "normal", "hard"] = "normal"
    weather: Literal["sunny", "rain", "snow"] = "sunny"
    home_formation: str = "4-3-3"
    away_formation: str = "4-3-3"
    home_tactics: str = "balanced"
    away_tactics: str = "balanced"


class CreateMatch(BaseModel):
    home_team_id: UUID
    away_team_id: UUID
    seed: int
    scenario: MatchScenario = Field(default_factory=MatchScenario)

    @model_validator(mode="after")
    def validate_teams(self):
        if self.home_team_id == self.away_team_id:
            raise ValueError("Home team and away team must be different")
        return self


class MatchResponse(BaseModel):
    id: UUID
    status: MatchStatus
    home_team_id: UUID
    away_team_id: UUID
    home_score: int
    away_score: int
    current_minute: int
    current_second: int
    seed: int
    scenario: MatchScenario
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MatchTeamResponse(BaseModel):
    id: UUID
    match_id: UUID
    team_id: UUID
    side: str
    formation: str
    tactics: dict
    lineup: dict
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class MatchEventResponse(BaseModel):
    id: UUID
    match_id: UUID
    sequence: int
    event_time_second: int
    event_type: EventType
    team_id: UUID
    player_id: UUID | None = None
    related_player_id: UUID | None = None
    start_x: float | None = None
    start_y: float | None = None
    end_x: float | None = None
    end_y: float | None = None
    outcome: str | None = None
    payload: dict
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DetailedMatchResponse(BaseModel):
    id: UUID
    status: MatchStatus
    home_team_id: UUID
    away_team_id: UUID
    home_score: int
    away_score: int
    current_minute: int
    current_second: int
    seed: int
    scenario: MatchScenario
    match_teams: list[MatchTeamResponse]
    match_events: list[MatchEventResponse]
    match_insights: list[MatchInsightResponse]
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
