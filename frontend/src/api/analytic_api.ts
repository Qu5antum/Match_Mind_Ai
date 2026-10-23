import api from './client';
import type {
  MatchAnalyticsResponse,
  MatchStatisticsResponse,
  TeamStatisticsOnlyResponse,
  PlayerMatchStatisticsResponse,
  ShotStatisticsResponse,
  KeyMomentResponse,
  PossessionStatisticsResponse,
  TeamPerformanceComparisonResponse,
} from '../types/analytic';

export const analyticsService = {
  async getMatchAnalytics(matchId: string): Promise<MatchAnalyticsResponse> {
    const response = await api.get<MatchAnalyticsResponse>(`/matches/${matchId}/analytics`);
    return response.data;
  },

  async getMatchStatistics(matchId: string): Promise<MatchStatisticsResponse> {
    const response = await api.get<MatchStatisticsResponse>(`/matches/${matchId}/analytics/statistics`);
    return response.data;
  },

  async getTeamStatistics(matchId: string, teamId: string): Promise<TeamStatisticsOnlyResponse> {
    const response = await api.get<TeamStatisticsOnlyResponse>(`/matches/${matchId}/analytics/teams/${teamId}`);
    return response.data;
  },

  async getPlayerStatistics(matchId: string, playerId: string): Promise<PlayerMatchStatisticsResponse> {
    const response = await api.get<PlayerMatchStatisticsResponse>(`/matches/${matchId}/analytics/players/${playerId}`);
    return response.data;
  },

  async getShotStatistics(matchId: string): Promise<Record<string, ShotStatisticsResponse>> {
    const response = await api.get<Record<string, ShotStatisticsResponse>>(`/matches/${matchId}/analytics/shots`);
    return response.data;
  },

  async getKeyMoments(matchId: string): Promise<KeyMomentResponse[]> {
    const response = await api.get<KeyMomentResponse[]>(`/matches/${matchId}/analytics/key-moments`);
    return response.data;
  },

  async getPossessionStatistics(matchId: string): Promise<PossessionStatisticsResponse> {
    const response = await api.get<PossessionStatisticsResponse>(`/matches/${matchId}/analytics/possession`);
    return response.data;
  },

  async getTeamPerformanceComparison(matchId: string): Promise<TeamPerformanceComparisonResponse> {
    const response = await api.get<TeamPerformanceComparisonResponse>(`/matches/${matchId}/analytics/team-performance`);
    return response.data;
  },
};