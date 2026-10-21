import api from './client';
import type {
  MatchEventResponse,
  MatchEventCreate,
  GetMatchEventsParams,
  MatchEventCountResponse,
  MatchEventsDeleteResponse,
} from '../types/match_event';
import type { EventType } from '../types/match';

export const matchEventService = {
  async createMatchEvent(matchId: string, data: MatchEventCreate): Promise<MatchEventResponse> {
    const response = await api.post<MatchEventResponse>(`/${matchId}/events`, data);
    return response.data;
  },

  async createMatchEvents(matchId: string, events: MatchEventCreate[]): Promise<MatchEventResponse[]> {
    const response = await api.post<MatchEventResponse[]>(`/${matchId}/events/bulk`, events);
    return response.data;
  },

  async getMatchEventCount(
    matchId: string,
    params?: {
      event_type?: EventType;
      team_id?: string;
      player_id?: string;
    }
  ): Promise<MatchEventCountResponse> {
    const response = await api.get<MatchEventCountResponse>(`/${matchId}/events/count`, { params });
    return response.data;
  },

  async deleteMatchEvents(matchId: string): Promise<MatchEventsDeleteResponse> {
    const response = await api.delete<MatchEventsDeleteResponse>(`/${matchId}/events`);
    return response.data;
  },

  async getMatchEvents(matchId: string, params?: GetMatchEventsParams): Promise<MatchEventResponse[]> {
    const response = await api.get<MatchEventResponse[]>(`/${matchId}/events`, { params });
    return response.data;
  },

  async getMatchEventsByType(
    matchId: string,
    eventType: EventType,
    params?: { offset?: number; limit?: number }
  ): Promise<MatchEventResponse[]> {
    const response = await api.get<MatchEventResponse[]>(`/${matchId}/events/by-type/${eventType}`, { params });
    return response.data;
  },

  async getPlayerMatchEvents(
    matchId: string,
    playerId: string,
    params?: { offset?: number; limit?: number }
  ): Promise<MatchEventResponse[]> {
    const response = await api.get<MatchEventResponse[]>(`/${matchId}/events/by-player/${playerId}`, { params });
    return response.data;
  },

  async getEventsAfterSequence(
    matchId: string,
    sequence: number,
    params?: { limit?: number; offset?: number }
  ): Promise<MatchEventResponse[]> {
    const response = await api.get<MatchEventResponse[]>(`/${matchId}/events/after/${sequence}`, { params });
    return response.data;
  },

  async getMatchEvent(eventId: string): Promise<MatchEventResponse> {
    const response = await api.get<MatchEventResponse>(`/events/${eventId}`);
    return response.data;
  },
};