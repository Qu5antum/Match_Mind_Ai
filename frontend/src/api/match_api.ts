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
    const response = await api.post<MatchResponse>('/match', data);
    return response.data;
  },

  async getMatches(params?: GetMatchesParams): Promise<MatchResponse[]> {
    const response = await api.get<MatchResponse[]>('/match', { params });
    return response.data;
  },

  async getMatch(matchId: string): Promise<MatchResponse> {
    const response = await api.get<MatchResponse>(`/match/${matchId}`);
    return response.data;
  },

  async getMatchDetail(matchId: string): Promise<DetailedMatchResponse> {
    const response = await api.get<DetailedMatchResponse>(`/match/${matchId}/detail`);
    return response.data;
  },

  async simulateMatch(matchId: string): Promise<MatchResponse> {
    const response = await api.post<MatchResponse>(`/match/${matchId}/simulate`);
    return response.data;
  },

  async playMatch(matchId: string): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(`/match/${matchId}/play`);
    return response.data;
  },

  async pauseMatch(matchId: string): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(`/match/${matchId}/pause`);
    return response.data;
  },

  async finishMatch(matchId: string): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(`/match/${matchId}/finish`);
    return response.data;
  },
};