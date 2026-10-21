import api from './client';
import type {
  MatchInsightResponse,
  MatchInsightCreate,
  GenerateMatchInsightsRequest,
  GetMatchInsightsParams,
  GetInsightsByMinuteParams,
} from '../types/match_insight';

export const matchInsightService = {
  async createInsight(data: MatchInsightCreate): Promise<MatchInsightResponse> {
    const response = await api.post<MatchInsightResponse>('/insights', data);
    return response.data;
  },

  async createInsights(data: MatchInsightCreate[]): Promise<MatchInsightResponse[]> {
    const response = await api.post<MatchInsightResponse[]>('/insights/bulk', data);
    return response.data;
  },

  async generateMatchInsights(
    matchId: string,
    data?: GenerateMatchInsightsRequest
  ): Promise<MatchInsightResponse[]> {
    const response = await api.post<MatchInsightResponse[]>(
      `/matches/${matchId}/insights/generate`,
      data || {}
    );
    return response.data;
  },

  async getMatchInsights(
    matchId: string,
    params?: GetMatchInsightsParams
  ): Promise<MatchInsightResponse[]> {
    const response = await api.get<MatchInsightResponse[]>(`/matches/${matchId}/insights`, { params });
    return response.data;
  },

  async getInsight(insightId: string): Promise<MatchInsightResponse> {
    const response = await api.get<MatchInsightResponse>(`/insights/${insightId}`);
    return response.data;
  },

  async getInsightsByMinute(
    matchId: string,
    params: GetInsightsByMinuteParams
  ): Promise<MatchInsightResponse[]> {
    const response = await api.get<MatchInsightResponse[]>(
      `/matches/${matchId}/insights/by-minute`,
      { params }
    );
    return response.data;
  },
};