import api from './client'; 
import type { 
  PlayerResponse, 
  CreatePlayer, 
  UpdatePlayer, 
  BulkCreatePlayers 
} from '../types/player';

export const playerService = {
  async createManyPlayers(data: BulkCreatePlayers): Promise<any> {
    const response = await api.post('/player/bulk', data);
    return response.data;
  },

  async createPlayer(data: CreatePlayer): Promise<PlayerResponse> {
    const response = await api.post<PlayerResponse>('/player', data);
    return response.data;
  },

  async getPlayer(playerId: string): Promise<PlayerResponse> {
    const response = await api.get<PlayerResponse>(`/player/${playerId}`);
    return response.data;
  },

  async updatePlayer(playerId: string, data: UpdatePlayer): Promise<PlayerResponse> {
    const response = await api.patch<PlayerResponse>(`/player/${playerId}`, data);
    return response.data;
  },

  async deletePlayer(playerId: string): Promise<void> {
    await api.delete(`/player/${playerId}`);
  },

  async getPlayersByTeam(teamId: string): Promise<PlayerResponse[]> {
    const response = await api.get<PlayerResponse[]>(`/team/${teamId}/players`);
    return response.data;
  },
};