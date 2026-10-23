import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { playersApi } from '../api/players'
import { teamsApi } from '../api/teams'
import PlayerCard from '../components/players/PlayerCard'
import TeamForm from '../components/teams/TeamForm'
import PageContainer from '../components/layout/PageContainer'
import type { PlayerResponse } from '../types/player'
import type { TeamCreate, TeamResponse } from '../types/team'
import type { UpdatePlayer } from '../types/player'
import type { MatchResponse } from '../types/match'

export default function TeamDetailsPage({ teamId, teams, matches, onRefresh, navigate }: {
  teamId: string
  teams: TeamResponse[]
  matches: MatchResponse[]
  onRefresh: () => Promise<void>
  navigate: (path: string) => void
}) {
  const team = teams.find((item) => item.id === teamId)
  const [players, setPlayers] = useState<PlayerResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [editing, setEditing] = useState(false)
  const [adding, setAdding] = useState(false)
  const [error, setError] = useState('')
  const [playerForm, setPlayerForm] = useState({ name: '', position: 'Midfielder' })
  const loadPlayers = useCallback(async () => {
    setLoading(true)
    try { setPlayers(await playersApi.getPlayersByTeam(teamId)); setError('') }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not load players.') }
    finally { setLoading(false) }
  }, [teamId])
  useEffect(() => { void loadPlayers() }, [loadPlayers])
  if (!team) return <div className="panel empty-state"><h3>Team not found</h3><button className="text-link" onClick={() => navigate('/teams')}>Back to teams ↗</button></div>

  const saveTeam = async (data: TeamCreate) => {
    setBusy(true); setError('')
    try { await teamsApi.updateTeam(teamId, data); await onRefresh(); setEditing(false) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not update team.') }
    finally { setBusy(false) }
  }
  const deletePlayer = async (player: PlayerResponse) => {
    if (!window.confirm(`Delete player "${player.name}"?`)) return
    try { await playersApi.deletePlayer(player.id); await loadPlayers() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not delete player.') }
  }
  const updatePlayer = async (player: PlayerResponse, changes: UpdatePlayer) => {
    await playersApi.updatePlayer(player.id, changes)
    await loadPlayers()
  }
  const deleteTeam = async () => {
    if (!window.confirm(`Delete team "${team.name}"?`)) return
    setBusy(true); setError('')
    try { await teamsApi.deleteTeam(teamId); await onRefresh(); navigate('/teams') }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not delete team.') }
    finally { setBusy(false) }
  }
  const addPlayer = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setBusy(true); setError('')
    try {
      await playersApi.createPlayer({ name: playerForm.name.trim(), position: playerForm.position, team_id: teamId, passing: 60, shooting: 60, dribbling: 60, defending: 60, pace: 60, stamina: 60, vision: 60 })
      setPlayerForm({ name: '', position: 'Midfielder' }); setAdding(false); await loadPlayers()
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not add player.') }
    finally { setBusy(false) }
  }
  const teamMatches = matches.filter((match) => match.home_team_id === teamId || match.away_team_id === teamId)
  return <PageContainer eyebrow="TEAM / PROFILE" title={team.name} description={`${team.short_name} · ${teamMatches.length} matches`}
    action={<><button className="button secondary" onClick={() => navigate('/teams')}>← All teams</button><button className="button secondary danger-button" disabled={busy} onClick={() => void deleteTeam()}>Delete</button><button className="button primary" onClick={() => setEditing((value) => !value)}>{editing ? 'Cancel' : 'Edit team'}</button></>}>
    {error && <div className="alert" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss">×</button></div>}
    {editing && <section className="panel form-panel"><TeamForm busy={busy} initialTeam={team} onSubmit={saveTeam} onCancel={() => setEditing(false)} /></section>}
    <div className="stats-grid">
      <Stat label="Squad" value={players.length} />
      <Stat label="Matches" value={teamMatches.length} />
      <Stat label="Wins" value={teamMatches.filter((match) => match.status === 'finished' && (match.home_team_id === teamId ? match.home_score > match.away_score : match.away_score > match.home_score)).length} />
      <Stat label="Goals scored" value={teamMatches.reduce((sum, match) => sum + (match.home_team_id === teamId ? match.home_score : match.away_score), 0)} />
    </div>
    <div className="page-subsection-heading"><div><h2>Team roster</h2><p>Players and their strengths</p></div><button className="button secondary" onClick={() => setAdding((value) => !value)}>＋ Add player</button></div>
    {adding && <form className="panel add-player-form" onSubmit={(event) => void addPlayer(event)}><label>Player name<input required value={playerForm.name} onChange={(event) => setPlayerForm((current) => ({ ...current, name: event.target.value }))} /></label><label>Position<select value={playerForm.position} onChange={(event) => setPlayerForm((current) => ({ ...current, position: event.target.value }))}><option>Goalkeeper</option><option>Defender</option><option>Midfielder</option><option>Forward</option></select></label><button className="button primary" disabled={busy}>{busy ? 'Adding...' : 'Save player'}</button></form>}
    {loading ? <p className="placeholder">Loading roster...</p> : players.length ? <div className="players-grid">{players.map((player) => <PlayerCard key={player.id} player={player} teamName={team.name} onDelete={(item) => void deletePlayer(item)} onUpdate={updatePlayer} />)}</div> : <div className="panel empty-state"><h3>Roster is empty</h3><p>Add players to build your team.</p></div>}
    <div className="page-subsection-heading"><div><h2>Match history</h2><p>Matches featuring this team</p></div></div>
    {teamMatches.map((match) => <button className="team-match-row" key={match.id} onClick={() => navigate(`/matches/${match.id}`)}>{match.home_score} : {match.away_score}<span>{match.created_at.slice(0, 10)}</span></button>)}
  </PageContainer>
}

function Stat({ label, value }: { label: string; value: number }) {
  return <article className="stat-card"><div className="stat-top">{label}</div><strong>{value.toLocaleString('en-US')}</strong></article>
}
