import { useState, type FormEvent } from 'react'
import type { PlayerResponse } from '../../types/player'
import type { UpdatePlayer } from '../../types/player'

export default function PlayerCard({ player, teamName, onDelete, onUpdate }: {
  player: PlayerResponse
  teamName: string
  onDelete?: (player: PlayerResponse) => void
  onUpdate?: (player: PlayerResponse, changes: UpdatePlayer) => Promise<void>
}) {
  const [editing, setEditing] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const rating = Math.round((player.passing + player.shooting + player.dribbling + player.defending + player.pace + player.stamina + player.vision) / 7)
  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!onUpdate) return
    const data = new FormData(event.currentTarget)
    setBusy(true); setError('')
    try {
      await onUpdate(player, { name: String(data.get('name')).trim(), position: String(data.get('position')) })
      setEditing(false)
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not update player.') }
    finally { setBusy(false) }
  }
  return <article className="panel player-card">
    <div className="player-card-top"><span className="player-avatar">{player.name.split(/\s+/).map((part) => part[0]).slice(0, 2).join('').toUpperCase()}</span><span className="player-rating"><b>{rating}</b><small>OVR</small></span></div>
    {editing ? <form className="player-edit-form" onSubmit={(event) => void save(event)}><label>Name<input name="name" required maxLength={100} defaultValue={player.name} /></label><label>Position<select name="position" defaultValue={player.position}><option>Goalkeeper</option><option>Defender</option><option>Midfielder</option><option>Forward</option></select></label><div className="form-actions"><button className="button primary" disabled={busy}>{busy ? 'Saving...' : 'Save'}</button><button type="button" className="button secondary" onClick={() => setEditing(false)}>Cancel</button></div>{error && <small className="inline-error">{error}</small>}</form> : <><h2>{player.name}</h2><p>{player.position} <span>·</span> {teamName}</p>
    <div className="player-attributes">{[['Pace', player.pace], ['Shooting', player.shooting], ['Passing', player.passing], ['Vision', player.vision]].map(([label, value]) => <div key={label}><span>{label}</span><b>{value}</b><i><em style={{ width: `${Math.max(0, Math.min(100, Number(value)))}%` }} /></i></div>)}</div>
    <div className="player-actions">{onUpdate && <button className="text-link" onClick={() => setEditing(true)}>Edit</button>}{onDelete && <button className="text-link player-delete" onClick={() => onDelete(player)}>Delete</button>}</div></>}
  </article>
}
