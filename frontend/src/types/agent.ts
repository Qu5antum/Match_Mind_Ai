import type { InsightType, Importance } from './match_insight';

export interface InsightEvidence {
  event_ids: string[];
  player_names: string[];
  supporting_stats: string[];
  explanation?: string | null;
}

export interface GeneratedMatchInsight {
  insight_type: InsightType;
  title: string;
  content: string;
  importance: Importance;
  minute?: number | null;
  evidence: InsightEvidence;
}

export interface GeneratedMatchInsights {
  insights: GeneratedMatchInsight[];
}

export interface GeneratedInsightExplanation {
  explanation: string; 
  significance: string;
  evidence_summary: string[];
  limitations: string[];
}

export interface MatchSummaryResponse {
  title: string;
  summary: string;
  key_takeaways: string[];
  decisive_moments: string[];
  limitations: string[];
}

export interface KeyMomentExplanation {
  explanation: string;
  significance: string;
  contributing_factors: string[];
  evidence_summary: string[];
  limitations: string[];
}

export interface MatchQuestionResponse {
  answer: string;
  supporting_facts: string[];
  limitations: string[];
}

export interface TacticalAnalysisResponse {
  overview: string;
  strengths: string[];
  weaknesses: string[];
  tactical_observations: string[];
  limitations: string[];
}

export interface TeamComparisonResponse {
  overview: string;
  advantages: string[];
  differences: string[];
  conclusion: string;
  limitations: string[];
}

export interface PlayerAnalysisResponse {
  overview: string;
  strengths: string[];
  weaknesses: string[];
  performance_facts: string[];
  limitations: string[];
}

export interface InsightPersonalizationResponse {
  title: string;
  explanation: string;
  key_points: string[];
}

export interface TeamRecommendationsResponse {
  overview: string;
  recommendations: string[];
  supporting_facts: string[];
  limitations: string[];
}

export interface ExplainInsightParams {
  language?: string;
  audience?: string; 
}

export interface MatchQuestionRequest {
  question: string; 
  language?: string; 
}

export interface AgentSummaryRequest {
  language?: string; 
}

export interface KeyMomentRequest {
  event_id: string;
  language?: string; 
}

export interface TacticalAnalysisRequest {
  team_id?: string | null;
  language?: string;
}

export interface PlayerAnalysisRequest {
  player_id: string;
  language?: string; 
}

export interface InsightPersonalizationRequest {
  audience?: string; 
  language?: string; 
}

export interface TeamRecommendationsRequest {
  team_id: string;
  language?: string; 
}