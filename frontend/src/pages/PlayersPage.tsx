import { useCallback, useEffect, useState } from 'react'
import { playersApi } from '../api/players'
import PlayerCard from '../components/players/PlayerCard'
import PageContainer from '../components/layout/PageContainer'
import type { PlayerResponse } from '../types/player'
import type { UpdatePlayer } from '../types/player'
import type { TeamResponse } from '../types/team'

export default function PlayersPage({ teams }: { teams: TeamResponse[] }) {
  const [players, setPlayers] = useState<PlayerResponse[]>([])
  const [teamFilter, setTeamFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const load = useCallback(async () => {
    if (!teams.length) { setPlayers([]); setLoading(false); return }
    setLoading(true)
    try { setPlayers((await Promise.all(teams.map((team) => playersApi.getPlayersByTeam(team.id)))).flat()); setError('') }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not load players.') }
    finally { setLoading(false) }
  }, [teams])
  useEffect(() => { void load() }, [load])
  const visible = players.filter((player) => !teamFilter || player.team_id === teamFilter)
  const teamMap = new Map(teams.map((team) => [team.id, team]))
  const remove = async (player: PlayerResponse) => {
    if (!window.confirm(`Delete player "${player.name}"?`)) return
    try { await playersApi.deletePlayer(player.id); await load() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not delete player.') }
  }
  const update = async (player: PlayerResponse, changes: UpdatePlayer) => {
    try { await playersApi.updatePlayer(player.id, changes); await load() }
    catch (cause) { throw new Error(cause instanceof Error ? cause.message : 'Could not update player.') }
  }
  return <PageContainer eyebrow="SQUADS" title="Players" description="Team rosters and individual player attributes.">
    {error && <div className="alert" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss">×</button></div>}
    <div className="filter-row"><span>{visible.length} players</span><label>Team<select value={teamFilter} onChange={(event) => setTeamFilter(event.target.value)}><option value="">All teams</option>{teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}</select></label></div>
    {loading ? <p className="placeholder">Loading team rosters...</p> : visible.length ? <div className="players-grid">{visible.map((player) => <PlayerCard key={player.id} player={player} teamName={teamMap.get(player.team_id)?.name ?? 'Team'} onDelete={(item) => void remove(item)} onUpdate={update} />)}</div> : <div className="panel empty-state"><h3>No players found</h3><p>Add players from a team's profile.</p></div>}
  </PageContainer>
}
