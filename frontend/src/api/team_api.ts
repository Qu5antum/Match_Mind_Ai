import api from './client';
import type { TeamResponse, TeamCreate, TeamUpdate, GetTeamsParams } from '../types/team';

export const teamService = {
  async createTeam(data: TeamCreate): Promise<TeamResponse> {
    const response = await api.post<TeamResponse>('/team', data);
    return response.data;
  },

  async getTeams(params?: GetTeamsParams): Promise<TeamResponse[]> {
    const response = await api.get<TeamResponse[]>('/team', { params });
    return response.data;
  },

  async getTeam(teamId: string): Promise<TeamResponse> {
    const response = await api.get<TeamResponse>(`/team/${teamId}`);
    return response.data;
  },

  async updateTeam(teamId: string, data: TeamUpdate): Promise<TeamResponse> {
    const response = await api.patch<TeamResponse>(`/team/${teamId}`, data);
    return response.data;
  },

  async deleteTeam(teamId: string): Promise<void> {
    await api.delete(`/team/${teamId}`);
  },
};