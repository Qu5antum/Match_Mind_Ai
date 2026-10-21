export interface TeamResponse {
  id: string; 
  name: string;
  short_name: string;
  created_at: string; 
  updated_at?: string | null;
}

export interface TeamCreate {
  name: string;
  short_name: string;
}

export interface TeamUpdate {
  name?: string | null;
  short_name?: string | null;
}

export interface GetTeamsParams {
  limit?: number;
  offset?: number;
}