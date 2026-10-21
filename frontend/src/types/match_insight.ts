export type InsightType = 
  | 'key_moment' 
  | 'team_performance' 
  | 'player_performance' 
  | 'tactical' 
  | 'prediction' 
  | 'player' 
  | 'recap' 
  | 'summary' 
  | string;

export type Importance = 'low' | 'medium' | 'high' | 'critical';

export interface MatchInsightResponse {
  id: string;
  match_id: string;
  insight_type: InsightType;
  title: string;
  content: string;
  importance: Importance;
  minute?: number | null;
  evidence: Record<string, any>;
  audience: string;
  language: string;
  model_name?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface MatchInsightResponse {
  id: string;
  match_id: string;
  insight_type: InsightType;
  title: string;
  content: string;
  importance: Importance;
  minute?: number | null;
  evidence: Record<string, any>;
  audience: string;
  language: string;
  model_name?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface MatchInsightCreate {
  match_id: string;
  insight_type: InsightType;
  title: string; 
  content: string; 
  importance: Importance;
  minute?: number | null; 
  evidence?: Record<string, any>;
}

export interface GenerateMatchInsightsRequest {
  language?: string; 
  audience?: string; 
}

export interface GetMatchInsightsParams {
  limit?: number; 
  offset?: number; 
  insight_type?: InsightType;
  importance?: Importance;
}

export interface GetInsightsByMinuteParams {
  start_minute: number; 
  end_minute: number; 
}