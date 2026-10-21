from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from src.database.models.match_insights import InsightType, Importance


class MatchInsightCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_id: UUID
    insight_type: InsightType
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    importance: Importance
    minute: int | None = Field(default=None, ge=0)
    evidence: dict = Field(default_factory=dict)


class GenerateMatchInsightsRequest(BaseModel):
    language: str = Field(default="en", min_length=2, max_length=10)
    audience: str = Field(default="general", min_length=2, max_length=20)


class MatchInsightResponse(BaseModel):
    id: UUID
    match_id: UUID
    insight_type: InsightType
    title: str
    content: str
    importance: Importance
    minute: int | None = None
    evidence: dict
    audience: str
    language: str
    model_name: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
