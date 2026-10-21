from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TeamStatisticsResponse(BaseModel):
    goals: int = Field(ge=0)
    shots: int = Field(ge=0)
    shots_on_target: int = Field(ge=0)
    shots_off_target: int = Field(ge=0)
    passes_attempted: int = Field(ge=0)
    passes_completed: int = Field(ge=0)
    pass_accuracy_percent: float | None = Field(default=None, ge=0, le=100)
    dribbles_attempted: int = Field(ge=0)
    dribbles_completed: int = Field(ge=0)
    dribble_success_percent: float | None = Field(default=None, ge=0, le=100)
    tackles: int = Field(ge=0)
    interceptions: int = Field(ge=0)
    fouls: int = Field(ge=0)
    corners: int = Field(ge=0)
    yellow_cards: int = Field(ge=0)
    red_cards: int = Field(ge=0)


class TeamAnalysisResponse(BaseModel):
    team_id: UUID
    statistics: TeamStatisticsResponse


class MatchTeamsAnalysisResponse(BaseModel):
    home: TeamAnalysisResponse
    away: TeamAnalysisResponse


class PlayerStatisticsResponse(BaseModel):
    player_id: UUID
    events_count: int = Field(ge=0)
    goals: int = Field(ge=0)
    shots: int = Field(ge=0)
    shots_on_target: int = Field(ge=0)
    passes_attempted: int = Field(ge=0)
    passes_completed: int = Field(ge=0)
    pass_accuracy_percent: float | None = Field(default=None, ge=0, le=100)
    dribbles_attempted: int = Field(ge=0)
    dribbles_completed: int = Field(ge=0)
    tackles: int = Field(ge=0)
    interceptions: int = Field(ge=0)


class ShotStatisticsResponse(BaseModel):
    shots: int = Field(ge=0)
    shots_on_target: int = Field(ge=0)
    goals: int = Field(ge=0)
    shot_accuracy_percent: float | None = Field(default=None, ge=0, le=100)
    conversion_percent: float | None = Field(default=None, ge=0, le=100)
    xg: float | None = Field(default=None, ge=0)
    xg_shots_count: int = Field(ge=0)


class KeyMomentEvidenceResponse(BaseModel):
    event_type: str
    outcome: str
    payload: dict[str, Any]


class KeyMomentResponse(BaseModel):
    type: str
    importance: Literal["low", "medium", "high", "critical"]
    reason: str
    event_ids: list[UUID]
    sequence: int = Field(ge=0)
    event_time_second: int = Field(ge=0)
    team_id: UUID
    player_id: UUID | None = None
    evidence: KeyMomentEvidenceResponse


class AnalyticsMetadataResponse(BaseModel):
    events_analyzed: int = Field(ge=0)
    algorithm_version: str
    possession_available: bool


class MatchAnalyticsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_id: UUID
    teams: MatchTeamsAnalysisResponse
    players: list[PlayerStatisticsResponse]
    shots: dict[str, ShotStatisticsResponse]
    key_moments: list[KeyMomentResponse]
    metadata: AnalyticsMetadataResponse


class MatchStatisticsResponse(BaseModel):
    home: TeamAnalysisResponse
    away: TeamAnalysisResponse


class TeamStatisticsOnlyResponse(TeamStatisticsResponse):
    pass


class PlayerMatchStatisticsResponse(PlayerStatisticsResponse):
    match_id: UUID


class PossessionUnavailableResponse(BaseModel):
    available: Literal[False]
    reason: str


class PossessionAvailableResponse(BaseModel):
    available: Literal[True]
    possession_seconds: dict[UUID, float]
    possession_percent: dict[UUID, float]
    total_seconds: float = Field(ge=0)


PossessionStatisticsResponse = (
    PossessionAvailableResponse | PossessionUnavailableResponse
)


class MetricComparisonResponse(BaseModel):
    home: int
    away: int
    difference_home_minus_away: int


class TeamPerformanceComparisonResponse(BaseModel):
    match_id: UUID
    comparison: dict[str, MetricComparisonResponse]
