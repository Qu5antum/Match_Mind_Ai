export interface TeamStatisticsResponse {
  goals: number;
  shots: number;
  shots_on_target: number;
  shots_off_target: number;
  passes_attempted: number;
  passes_completed: number;
  pass_accuracy_percent?: number | null;
  dribbles_attempted: number;
  dribbles_completed: number;
  dribble_success_percent?: number | null;
  tackles: number;
  interceptions: number;
  fouls: number;
  corners: number;
  yellow_cards: number;
  red_cards: number;
}

export interface TeamAnalysisResponse {
  team_id: string;
  statistics: TeamStatisticsResponse;
}

export interface MatchTeamsAnalysisResponse {
  home: TeamAnalysisResponse;
  away: TeamAnalysisResponse;
}

export interface PlayerStatisticsResponse {
  player_id: string;
  events_count: number;
  goals: number;
  shots: number;
  shots_on_target: number;
  passes_attempted: number;
  passes_completed: number;
  pass_accuracy_percent?: number | null;
  dribbles_attempted: number;
  dribbles_completed: number;
  tackles: number;
  interceptions: number;
}

export interface ShotStatisticsResponse {
  shots: number;
  shots_on_target: number;
  goals: number;
  shot_accuracy_percent?: number | null;
  conversion_percent?: number | null;
  xg?: number | null;
  xg_shots_count: number;
}

export interface KeyMomentEvidenceResponse {
  event_type: string;
  outcome: string;
  payload: Record<string, any>;
}

export interface KeyMomentResponse {
  type: string;
  importance: 'low' | 'medium' | 'high' | 'critical';
  reason: string;
  event_ids: string[];
  sequence: number;
  event_time_second: number;
  team_id: string;
  player_id?: string | null;
  evidence: KeyMomentEvidenceResponse;
}

export interface AnalyticsMetadataResponse {
  events_analyzed: number;
  algorithm_version: string;
  possession_available: boolean;
}

export interface MatchAnalyticsResponse {
  match_id: string;
  teams: MatchTeamsAnalysisResponse;
  players: PlayerStatisticsResponse[];
  shots: Record<string, ShotStatisticsResponse>;
  key_moments: KeyMomentResponse[];
  metadata: AnalyticsMetadataResponse;
}

export interface MatchStatisticsResponse {
  home: TeamAnalysisResponse;
  away: TeamAnalysisResponse;
}

export interface TeamStatisticsOnlyResponse extends TeamStatisticsResponse {}

export interface PlayerMatchStatisticsResponse extends PlayerStatisticsResponse {
  match_id: string;
}

export interface PossessionUnavailableResponse {
  available: false;
  reason: string;
}

export interface PossessionAvailableResponse {
  available: true;
  possession_seconds: Record<string, number>; 
  possession_percent: Record<string, number>; 
  total_seconds: number;
}

export type PossessionStatisticsResponse = 
  | PossessionAvailableResponse 
  | PossessionUnavailableResponse;

export interface MetricComparisonResponse {
  home: number;
  away: number;
  difference_home_minus_away: number;
}

export interface TeamPerformanceComparisonResponse {
  match_id: string;
  comparison: Record<string, MetricComparisonResponse>;
}