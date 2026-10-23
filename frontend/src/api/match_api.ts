import api from './client';
import type {
  CreateMatch,
  MatchResponse,
  DetailedMatchResponse,
  GetMatchesParams,
  MessageResponse,
} from '../types/match';

export const matchService = {
  async createMatch(data: CreateMatch): Promise<MatchResponse> {
    const response = await api.post<MatchResponse>('/matches', data);
    return response.data;
  },

  async getMatches(params?: GetMatchesParams): Promise<MatchResponse[]> {
    const response = await api.get<MatchResponse[]>('/matches', { params });
    return response.data;
  },

  async getMatch(matchId: string): Promise<MatchResponse> {
    const response = await api.get<MatchResponse>(`/matches/${matchId}`);
    return response.data;
  },

  async getMatchDetail(matchId: string): Promise<DetailedMatchResponse> {
    const response = await api.get<DetailedMatchResponse>(`/matches/${matchId}/detail`);
    return response.data;
  },

  async simulateMatch(matchId: string): Promise<MatchResponse> {
    const response = await api.post<MatchResponse>(`/matches/${matchId}/simulate`);
    return response.data;
  },

  async playMatch(matchId: string): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(`/matches/${matchId}/play`);
    return response.data;
  },

  async pauseMatch(matchId: string): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(`/matches/${matchId}/pause`);
    return response.data;
  },

  async finishMatch(matchId: string): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(`/matches/${matchId}/finish`);
    return response.data;
  },
};