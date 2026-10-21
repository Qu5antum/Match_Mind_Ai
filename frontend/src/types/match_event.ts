import type { EventType } from './match'; 

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

export interface MatchEventCreate {
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
  payload?: Record<string, any>;
}

export interface GetMatchEventsParams {
  offset?: number; 
  limit?: number; 
  event_type?: EventType;
  team_id?: string;
  player_id?: string;
  after_sequence?: number;
}

export interface MatchEventCountResponse {
  count: number;
}

export interface MatchEventsDeleteResponse {
  deleted_count: number;
}