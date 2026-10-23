import PageContainer from '../components/layout/PageContainer'
import MatchCard from '../components/matches/MatchCard'
import type { MatchResponse } from '../types/match'
import type { TeamResponse } from '../types/team'

export default function MatchesPage({ matches, teams, search, navigate }: {
  matches: MatchResponse[]
  teams: TeamResponse[]
  search: string
  navigate: (path: string) => void
}) {
  const teamMap = new Map(teams.map((team) => [team.id, team]))
  const query = search.trim().toLocaleLowerCase()
  const visible = matches.filter((match) => !query || `${teamMap.get(match.home_team_id)?.name ?? ''} ${teamMap.get(match.away_team_id)?.name ?? ''} ${match.status}`.toLocaleLowerCase().includes(query))
  return <PageContainer eyebrow="MATCH LIBRARY" title="Matches" description="Create fixtures and explore match statistics."
    action={<button className="button primary" onClick={() => navigate('/matches/new')}>＋ New match</button>}>
    <section className="panel match-list"><div className="panel-heading"><div><h2>All fixtures</h2><p>{visible.length} matches</p></div></div>
      {visible.length ? visible.map((match) => <MatchCard key={match.id} match={match} home={teamMap.get(match.home_team_id)} away={teamMap.get(match.away_team_id)} onClick={() => navigate(`/matches/${match.id}`)} />) :
        <div className="empty-state"><span>◉</span><h3>No matches found</h3><p>Change your search or create a new fixture.</p><button className="text-link" onClick={() => navigate('/matches/new')}>Create match ↗</button></div>}
    </section>
  </PageContainer>
}
