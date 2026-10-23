import { useState } from 'react'
import PageContainer from '../components/layout/PageContainer'
import TeamCard from '../components/teams/TeamCard'
import TeamForm from '../components/teams/TeamForm'
import { teamsApi } from '../api/teams'
import type { MatchResponse } from '../types/match'
import type { TeamCreate, TeamResponse } from '../types/team'

export default function TeamsPage({ teams, matches, navigate, onRefresh }: {
  teams: TeamResponse[]
  matches: MatchResponse[]
  navigate: (path: string) => void
  onRefresh: () => Promise<void>
}) {
  const [creating, setCreating] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const create = async (data: TeamCreate) => {
    setBusy(true); setError('')
    try { await teamsApi.createTeam(data); await onRefresh(); setCreating(false) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not create team.') }
    finally { setBusy(false) }
  }
  return <PageContainer eyebrow="SQUAD MANAGEMENT" title="Teams" description="Manage clubs and participants in your simulations."
    action={<button className="button primary" onClick={() => setCreating((value) => !value)}>＋ Add team</button>}>
    {error && <div className="alert" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss">×</button></div>}
    {creating && <section className="panel form-panel"><h2>New team</h2><TeamForm busy={busy} onSubmit={create} onCancel={() => setCreating(false)} /></section>}
    {teams.length ? <div className="teams-grid">{teams.map((team) => <TeamCard key={team.id} team={team} matches={matches} onClick={() => navigate(`/teams/${team.id}`)} />)}</div> :
      <div className="panel empty-state"><span>♙</span><h3>No teams yet</h3><p>Add teams to create your first match.</p><button className="text-link" onClick={() => setCreating(true)}>Add a team ↗</button></div>}
  </PageContainer>
}
