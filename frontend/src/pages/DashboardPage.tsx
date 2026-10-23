import PageContainer from '../components/layout/PageContainer'
import MatchCard from '../components/matches/MatchCard'
import type { MatchResponse } from '../types/match'
import type { TeamResponse } from '../types/team'

export default function DashboardPage({ teams, matches, navigate }: {
  teams: TeamResponse[]
  matches: MatchResponse[]
  navigate: (path: string) => void
}) {
  const teamMap = new Map(teams.map((team) => [team.id, team]))
  const goals = matches.reduce((total, match) => total + match.home_score + match.away_score, 0)
  return <PageContainer eyebrow="COMMAND CENTER" title={<>Welcome to <em>MatchMind.</em></>} description="Your hub for football data and tactical insights."
    action={<button className="button primary" onClick={() => navigate('/matches/new')}>＋ Create match</button>}>
    <div className="stats-grid">
      <Stat title="Total matches" value={matches.length} note="In your library" icon="◉" tone="violet" />
      <Stat title="Completed" value={matches.filter((match) => match.status === 'finished').length} note="Full analytics available" icon="◷" tone="mint" />
      <Stat title="Goals scored" value={goals} note="Across all matches" icon="✳" tone="amber" />
      <Stat title="Teams" value={teams.length} note="In your workspace" icon="♙" tone="blue" />
    </div>
    <div className="overview-grid">
      <section className="panel recent"><div className="panel-heading"><div><h2>Recent matches</h2><p>Follow your match simulations</p></div><button className="text-link" onClick={() => navigate('/matches')}>All matches ↗</button></div>
        {matches.length ? [...matches].slice(0, 5).map((match) => <MatchCard key={match.id} match={match} home={teamMap.get(match.home_team_id)} away={teamMap.get(match.away_team_id)} onClick={() => navigate(`/matches/${match.id}`)} />) :
          <Empty title="No matches yet" text="Create your first fixture and start a simulation." action="Create match" onClick={() => navigate('/matches/new')} />}
      </section>
      <section className="panel promo"><div className="promo-spark">✳</div><div className="eyebrow">YOUR AI ASSISTANT</div><h2>Play smarter.<br />Analyze deeper.</h2><p>Get tactical breakdowns and clear insights from match events.</p><button className="button light" onClick={() => navigate('/matches')}>Explore matches and AI analysis →</button><span className="promo-orb" /></section>
    </div>
    <button className="quick-strip" onClick={() => navigate('/teams')}><span className="quick-icon">♙</span><span><b>Manage your teams</b><small>Create clubs and set up new fixtures.</small></span><span className="text-link">View teams ↗</span></button>
  </PageContainer>
}

function Stat({ title, value, note, icon, tone }: { title: string; value: number; note: string; icon: string; tone: string }) {
  return <article className="stat-card"><div className="stat-top"><span>{title}</span><i className={`stat-icon ${tone}`}>{icon}</i></div><strong>{value.toLocaleString('en-US')}</strong><small>{note}</small></article>
}

function Empty({ title, text, action, onClick }: { title: string; text: string; action: string; onClick: () => void }) {
  return <div className="empty-state"><span>◉</span><h3>{title}</h3><p>{text}</p><button className="text-link" onClick={onClick}>{action} ↗</button></div>
}
