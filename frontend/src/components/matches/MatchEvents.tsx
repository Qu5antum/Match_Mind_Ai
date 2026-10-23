import type { MatchEventResponse } from '../../types/match_event'
import type { TeamResponse } from '../../types/team'

const eventNames: Record<string, string> = { goal: 'Goal', shot: 'Shot', yellow_card: 'Yellow card', red_card: 'Red card', substitution: 'Substitution', penalty_scored: 'Penalty scored', penalty_missed: 'Penalty missed', save: 'Save', foul: 'Foul', corner: 'Corner', half_time: 'Half-time', period_start: 'Period started', period_end: 'Period ended' }

export default function MatchEvents({ events, teams }: { events: MatchEventResponse[]; teams: Map<string, TeamResponse> }) {
  if (!events.length) return <p className="placeholder">No events yet. Simulate the match to see its timeline.</p>
  return <div className="events-list">{events.map((event) => {
    const name = eventNames[event.event_type] ?? event.event_type.replaceAll('_', ' ')
    const team = teams.get(event.team_id)
    const description = event.outcome || (typeof event.payload.description === 'string' ? event.payload.description : '')
    return <article className="event-item" key={event.id}><span className={`event-marker ${event.event_type === 'goal' || event.event_type === 'penalty_scored' ? 'goal-marker' : ''}`} /><time>{Math.floor(event.event_time_second / 60)}&apos;</time><div><b>{name}</b>{description && <p>{description}</p>}</div><small>{team?.short_name ?? '—'}</small></article>
  })}</div>
}
