from pydantic import BaseModel, Field

from src.database.models.match_insights import InsightType, Importance
from uuid import UUID


class InsightEvidence(BaseModel):
    event_ids: list[str]
    player_names: list[str]
    supporting_stats: list[str]
    explanation: str | None


class GeneratedMatchInsight(BaseModel):
    insight_type: InsightType
    title: str
    content: str
    importance: Importance
    minute: int | None
    evidence: InsightEvidence


class GeneratedMatchInsights(BaseModel):
    insights: list[GeneratedMatchInsight]

class GeneratedInsightExplanation(BaseModel):
    explanation: str = Field(min_length=1, max_length=3000)
    significance: str = Field(min_length=1, max_length=1500)
    evidence_summary: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class MatchSummaryResponse(BaseModel):
    title: str
    summary: str
    key_takeaways: list[str] = Field(default_factory=list)
    decisive_moments: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class KeyMomentExplanation(BaseModel):
    explanation: str
    significance: str
    contributing_factors: list[str] = Field(default_factory=list)
    evidence_summary: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class MatchQuestionResponse(BaseModel):
    answer: str
    supporting_facts: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class TacticalAnalysisResponse(BaseModel):
    overview: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    tactical_observations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class TeamComparisonResponse(BaseModel):
    overview: str
    advantages: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)
    conclusion: str
    limitations: list[str] = Field(default_factory=list)


class PlayerAnalysisResponse(BaseModel):
    overview: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    performance_facts: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class InsightPersonalizationResponse(BaseModel):
    title: str
    explanation: str
    key_points: list[str] = Field(default_factory=list)


class TeamRecommendationsResponse(BaseModel):
    overview: str
    recommendations: list[str] = Field(default_factory=list)
    supporting_facts: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class MatchQuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    language: str = Field(default="en", min_length=2, max_length=10)


class AgentSummaryRequest(BaseModel):
    language: str = Field(default="en", min_length=2, max_length=10)


class KeyMomentRequest(BaseModel):
    event_id: UUID
    language: str = Field(default="en", min_length=2, max_length=10)


class TacticalAnalysisRequest(BaseModel):
    team_id: UUID | None = None
    language: str = Field(default="en", min_length=2, max_length=10)


class PlayerAnalysisRequest(BaseModel):
    player_id: UUID
    language: str = Field(default="en", min_length=2, max_length=10)


class InsightPersonalizationRequest(BaseModel):
    audience: str = Field(default="beginner", min_length=2, max_length=20)
    language: str = Field(default="en", min_length=2, max_length=10)


class TeamRecommendationsRequest(BaseModel):
    team_id: UUID
    language: str = Field(default="en", min_length=2, max_length=10)


class GeneratedInsightExplanation(BaseModel):
    explanation: str = Field(min_length=1, max_length=3000)
    significance: str = Field(min_length=1, max_length=1500)
    evidence_summary: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class MatchSummaryResponse(BaseModel):
    title: str
    summary: str
    key_takeaways: list[str] = Field(default_factory=list)
    decisive_moments: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class KeyMomentExplanation(BaseModel):
    explanation: str
    significance: str
    contributing_factors: list[str] = Field(default_factory=list)
    evidence_summary: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class MatchQuestionResponse(BaseModel):
    answer: str
    supporting_facts: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class TacticalAnalysisResponse(BaseModel):
    overview: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    tactical_observations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class TeamComparisonResponse(BaseModel):
    overview: str
    advantages: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)
    conclusion: str
    limitations: list[str] = Field(default_factory=list)


class PlayerAnalysisResponse(BaseModel):
    overview: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    performance_facts: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class InsightPersonalizationResponse(BaseModel):
    title: str
    explanation: str
    key_points: list[str] = Field(default_factory=list)


class TeamRecommendationsResponse(BaseModel):
    overview: str
    recommendations: list[str] = Field(default_factory=list)
    supporting_facts: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
