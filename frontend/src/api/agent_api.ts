import api from './client';
import type {
  GeneratedInsightExplanation,
  MatchSummaryResponse,
  KeyMomentExplanation,
  MatchQuestionResponse,
  TacticalAnalysisResponse,
  TeamComparisonResponse,
  PlayerAnalysisResponse,
  InsightPersonalizationResponse,
  TeamRecommendationsResponse,
  ExplainInsightParams,
  MatchQuestionRequest,
  AgentSummaryRequest,
  KeyMomentRequest,
  TacticalAnalysisRequest,
  PlayerAnalysisRequest,
  InsightPersonalizationRequest,
  TeamRecommendationsRequest,
} from '../types/agent';

export const agentService = {
  async explainInsight(
    insightId: string,
    params?: ExplainInsightParams
  ): Promise<GeneratedInsightExplanation> {
    const response = await api.post<GeneratedInsightExplanation>(
      `/insights/${insightId}/explain`,
      null,
      { params }
    );
    return response.data;
  },

  async summarizeMatch(
    matchId: string,
    data?: AgentSummaryRequest
  ): Promise<MatchSummaryResponse> {
    const response = await api.post<MatchSummaryResponse>(
      `/matches/${matchId}/agent/summary`,
      data || {}
    );
    return response.data;
  },

  async askAboutMatch(
    matchId: string,
    data: MatchQuestionRequest
  ): Promise<MatchQuestionResponse> {
    const response = await api.post<MatchQuestionResponse>(
      `/matches/${matchId}/agent/ask`,
      data
    );
    return response.data;
  },

  async explainKeyMoment(
    matchId: string,
    data: KeyMomentRequest
  ): Promise<KeyMomentExplanation> {
    const response = await api.post<KeyMomentExplanation>(
      `/matches/${matchId}/agent/key-moments/explain`,
      data
    );
    return response.data;
  },

  async generateTacticalAnalysis(
    matchId: string,
    data?: TacticalAnalysisRequest
  ): Promise<TacticalAnalysisResponse> {
    const response = await api.post<TacticalAnalysisResponse>(
      `/matches/${matchId}/agent/tactical-analysis`,
      data || {}
    );
    return response.data;
  },

  async compareMatchTeams(
    matchId: string,
    data?: AgentSummaryRequest
  ): Promise<TeamComparisonResponse> {
    const response = await api.post<TeamComparisonResponse>(
      `/matches/${matchId}/agent/team-comparison`,
      data || {}
    );
    return response.data;
  },

  async analyzePlayer(
    matchId: string,
    data: PlayerAnalysisRequest
  ): Promise<PlayerAnalysisResponse> {
    const response = await api.post<PlayerAnalysisResponse>(
      `/matches/${matchId}/agent/player-analysis`,
      data
    );
    return response.data;
  },

  async personalizeInsight(
    insightId: string,
    data?: InsightPersonalizationRequest
  ): Promise<InsightPersonalizationResponse> {
    const response = await api.post<InsightPersonalizationResponse>(
      `/insights/${insightId}/personalize`,
      data || {}
    );
    return response.data;
  },

  async generateTeamRecommendations(
    matchId: string,
    data: TeamRecommendationsRequest
  ): Promise<TeamRecommendationsResponse> {
    const response = await api.post<TeamRecommendationsResponse>(
      `/matches/${matchId}/agent/recommendations`,
      data
    );
    return response.data;
  },
};