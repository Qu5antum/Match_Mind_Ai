export interface PlayerResponse {
  id: string;
  name: string;
  position: string;
  team_id: string;
  passing: number;
  shooting: number;
  dribbling: number;
  defending: number;
  pace: number;
  stamina: number;
  vision: number;
  created_at: string;
  updated_at?: string | null;
}

export interface CreatePlayer {
  name: string;
  position: string;
  team_id: string;
  passing: number;
  shooting: number;
  dribbling: number;
  defending: number;
  pace: number;
  stamina: number;
  vision: number;
}

export interface UpdatePlayer {
  name?: string | null;
  position?: string | null;
  team_id?: string | null;
  passing?: number | null;
  shooting?: number | null;
  dribbling?: number | null;
  defending?: number | null;
  pace?: number | null;
  stamina?: number | null;
  vision?: number | null;
}

export interface BulkCreatePlayers {
  players: CreatePlayer[];
}