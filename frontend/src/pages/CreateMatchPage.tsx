import { useState, type FormEvent } from 'react'
import { matchesApi } from '../api/matches'
import PageContainer from '../components/layout/PageContainer'
import type { TeamResponse } from '../types/team'

export default function CreateMatchPage({ teams, navigate }: { teams: TeamResponse[]; navigate: (path: string) => void }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [seed, setSeed] = useState(() => Math.floor(Math.random() * 1_000_000))
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const home = String(form.get('home_team_id'))
    const away = String(form.get('away_team_id'))
    if (home === away) { setError('Select two different teams.'); return }
    if (!Number.isSafeInteger(seed) || seed < 0) { setError('Enter a non-negative integer seed.'); return }
    setBusy(true); setError('')
    try {
      const created = await matchesApi.createMatch({
        home_team_id: home, away_team_id: away, seed,
        scenario: {
          duration_minutes: Number(form.get('duration_minutes')) as 90 | 120,
          difficulty: String(form.get('difficulty')) as 'easy' | 'normal' | 'hard',
          weather: String(form.get('weather')) as 'sunny' | 'rain' | 'snow',
          home_formation: String(form.get('formation')) || '4-3-3',
          away_formation: String(form.get('formation')) || '4-3-3',
          home_tactics: 'balanced', away_tactics: 'balanced',
        },
      })
      navigate(`/matches/${created.id}`)
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not create match.') }
    finally { setBusy(false) }
  }
  return <PageContainer eyebrow="NEW FIXTURE" title="Create match" description="Configure the game and start your simulation."
    action={<button className="button secondary" onClick={() => navigate('/matches')}>← Back to matches</button>}>
    {error && <div className="alert" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss">×</button></div>}
    {teams.length < 2 ? <div className="panel empty-state"><h3>At least two teams are required</h3><p>Add teams before creating a match.</p><button className="button primary" onClick={() => navigate('/teams')}>View teams</button></div> :
      <form className="panel create-match-form" onSubmit={(event) => void submit(event)}>
        <div className="form-team-selects"><label>Home team<select name="home_team_id" required defaultValue=""><option value="" disabled>Select a team</option>{teams.map((team) => <option key={team.id} value={team.id}>{team.name} ({team.short_name})</option>)}</select></label><span className="versus">VS</span><label>Away team<select name="away_team_id" required defaultValue=""><option value="" disabled>Select a team</option>{teams.map((team) => <option key={team.id} value={team.id}>{team.name} ({team.short_name})</option>)}</select></label></div>
        <div className="form-divider" /><h2>Simulation settings</h2>
        <div className="form-row"><label>Duration<select name="duration_minutes"><option value="90">90 minutes</option><option value="120">120 minutes</option></select></label><label>Difficulty<select name="difficulty"><option value="normal">Normal</option><option value="easy">Easy</option><option value="hard">Hard</option></select></label></div>
        <div className="form-row"><label>Weather<select name="weather"><option value="sunny">Sunny</option><option value="rain">Rain</option><option value="snow">Snow</option></select></label><label>Formation<select name="formation"><option>4-3-3</option><option>4-4-2</option><option>3-5-2</option><option>4-2-3-1</option></select></label></div>
        <label>Simulation seed<input name="seed" type="number" min="0" step="1" required value={seed} onChange={(event) => setSeed(Number(event.target.value))} /><small className="field-help">Use the same seed to reproduce a simulation.</small></label>
        <button className="button primary" disabled={busy}>{busy ? 'Creating match...' : 'Create match'}</button>
      </form>}
  </PageContainer>
}
