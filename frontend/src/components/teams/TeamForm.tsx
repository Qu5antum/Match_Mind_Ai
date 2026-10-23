import type { FormEvent } from 'react'
import type { TeamCreate } from '../../types/team'
import type { TeamResponse } from '../../types/team'

export default function TeamForm({ busy, onSubmit, onCancel, initialTeam }: {
  busy: boolean
  onSubmit: (team: TeamCreate) => Promise<void>
  onCancel?: () => void
  initialTeam?: TeamResponse
}) {
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    void onSubmit({ name: String(data.get('name')).trim(), short_name: String(data.get('short_name')).trim().toUpperCase() })
  }
  return <form className="form-stack" onSubmit={submit}>
    <label>Team name<input name="name" required maxLength={100} defaultValue={initialTeam?.name} placeholder="e.g. Northern Stars" /></label>
    <label>Short name<input name="short_name" required maxLength={10} defaultValue={initialTeam?.short_name} placeholder="NTR" /></label>
    <div className="form-actions"><button className="button primary" disabled={busy}>{busy ? 'Saving...' : initialTeam ? 'Save changes' : 'Add team'}</button>{onCancel && <button type="button" className="button secondary" onClick={onCancel}>Cancel</button>}</div>
  </form>
}
