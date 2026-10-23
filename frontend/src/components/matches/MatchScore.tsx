import type { MatchResponse } from '../../types/match'
import type { TeamResponse } from '../../types/team'

export const statusLabels: Record<string, string> = { created: 'Created', simulating: 'Simulating', ready: 'Ready', playing: 'Live', paused: 'Paused', finished: 'Finished', failed: 'Failed' }

export default function MatchScore({ match, home, away }: {
  match: MatchResponse
  home?: TeamResponse
  away?: TeamResponse
}) {
  return <div className="scoreboard">
    <div className="score-team"><span className="crest">{(home?.short_name ?? 'HM').slice(0, 3)}</span><b>{home?.name ?? 'Home'}</b><small>Home</small></div>
    <div className="score">{match.home_score}<i>:</i>{match.away_score}<small>{match.current_minute}&apos; {String(match.current_second).padStart(2, '0')}&quot;</small></div>
    <div className="score-team"><span className="crest away">{(away?.short_name ?? 'AW').slice(0, 3)}</span><b>{away?.name ?? 'Away'}</b><small>Away</small></div>
  </div>
}
