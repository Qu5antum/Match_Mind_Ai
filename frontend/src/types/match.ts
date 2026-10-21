import type { MatchInsightResponse } from "./match_insight";

export type MatchStatus = 
  | 'created' 
  | 'simulating' 
  | 'ready' 
  | 'playing' 
  | 'paused' 
  | 'finished' 
  | 'failed';

export type EventType = 
  | 'general' | 'period_start' | 'period_end' | 'kick_off' 
  | 'half_time' | 'added_time' | 'extra_time_start' | 'extra_time_end' 
  | 'substitution' | 'pass' | 'carry' | 'dribble' | 'ball_recovery' 
  | 'miscontrol' | 'dispossessed' | 'shot' | 'goal' | 'own_goal' 
  | 'cross' | 'hit_woodwork' | 'offside' | 'tackle' | 'interception' 
  | 'clearance' | 'block' | 'pressure' | 'duel' | 'aerial_duel' 
  | 'save' | 'throw_in' | 'free_kicks' | 'free_kick' | 'penalty' 
  | 'penalty_scored' | 'penalty_missed' | 'penalty_saved' | 'goal_kick' 
  | 'corner' | 'foul' | 'yellow_card' | 'red_card' | 'injury' 
  | 'var_review' | 'penalty_shootout' | string;

export interface MatchScenario {
  duration_minutes: 90 | 120;
  difficulty: 'easy' | 'normal' | 'hard';
  weather: 'sunny' | 'rain' | 'snow';
  home_formation: string;
  away_formation: string;
  home_tactics: string;
  away_tactics: string;
}

export interface CreateMatch {
  home_team_id: string;
  away_team_id: string;
  seed: number;
  scenario?: MatchScenario;
}

export interface GetMatchesParams {
  limit?: number; 
  offset?: number; 
}

export interface MatchResponse {
  id: string;
  status: MatchStatus;
  home_team_id: string;
  away_team_id: string;
  home_score: number;
  away_score: number;
  current_minute: number;
  current_second: number;
  seed: number;
  scenario: MatchScenario;
  created_at: string;
  updated_at?: string | null;
}

export interface MatchTeamResponse {
  id: string;
  match_id: string;
  team_id: string;
  side: string;
  formation: string;
  tactics: Record<string, any>;
  lineup: Record<string, any>;
  created_at: string;
  updated_at?: string | null;
}

export interface MatchEventResponse {
  id: string;
  match_id: string;
  sequence: number;
  event_time_second: number;
  event_type: EventType;
  team_id: string;
  player_id?: string | null;
  related_player_id?: string | null;
  start_x?: number | null;
  start_y?: number | null;
  end_x?: number | null;
  end_y?: number | null;
  outcome?: string | null;
  payload: Record<string, any>;
  created_at: string;
  updated_at?: string | null;
}


export interface DetailedMatchResponse extends MatchResponse {
  match_teams: MatchTeamResponse[];
  match_events: MatchEventResponse[];
  match_insights: MatchInsightResponse[];
}

export interface MessageResponse {
  message: string;
}