import type { TeamResponse } from '../../types/team'

export default function TeamCard({ team, matches, onClick }: {
  team: TeamResponse
  matches: { home_team_id: string; away_team_id: string; home_score: number; away_score: number; status: string }[]
  onClick: () => void
}) {
  const games = matches.filter((match) => match.home_team_id === team.id || match.away_team_id === team.id)
  const wins = games.filter((match) => match.status === 'finished' && (match.home_team_id === team.id ? match.home_score > match.away_score : match.away_score > match.home_score)).length
  const goals = games.reduce((sum, match) => sum + (match.home_team_id === team.id ? match.home_score : match.away_score), 0)
  return <button className="panel team-card team-card-button" onClick={onClick}>
    <span className={`crest crest-${team.name.length % 4}`}>{team.short_name.slice(0, 3)}</span>
    <h2>{team.name}</h2><small className="team-code">{team.short_name}</small>
    <div className="team-stats"><span><b>{games.length}</b><small>Matches</small></span><span><b>{wins}</b><small>Wins</small></span><span><b>{goals}</b><small>Goals</small></span></div>
  </button>
}
