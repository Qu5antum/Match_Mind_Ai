import type { MatchResponse } from '../../types/match'
import type { TeamResponse } from '../../types/team'
import { statusLabels } from './MatchScore'

export default function MatchCard({ match, home, away, active, onClick }: {
  match: MatchResponse
  home?: TeamResponse
  away?: TeamResponse
  active?: boolean
  onClick: () => void
}) {
  return <button className={`match-row ${active ? 'selected' : ''}`} onClick={onClick}>
    <span className={`live-dot ${match.status === 'playing' ? 'is-live' : ''}`} />
    <span className="teams-score"><b>{home?.short_name ?? 'HOME'}</b><strong>{match.home_score} : {match.away_score}</strong><b>{away?.short_name ?? 'AWAY'}</b></span>
    <span className="match-names">{home?.name ?? 'Home'} <i>vs</i> {away?.name ?? 'Away'}</span>
    <span className={`status ${match.status}`}>{statusLabels[match.status] ?? match.status}</span><span className="row-arrow">↗</span>
  </button>
}
