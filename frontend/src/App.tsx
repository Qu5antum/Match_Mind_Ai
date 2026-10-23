import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'
import { matchesApi } from './api/matches'
import { teamsApi } from './api/teams'
import Navbar from './components/layout/Navbar'
import Sidebar from './components/layout/Sidebar'
import CreateMatchPage from './pages/CreateMatchPage'
import DashboardPage from './pages/DashboardPage'
import MatchDetailsPage from './pages/MatchDetailsPage'
import MatchesPage from './pages/MatchesPage'
import NotFoundPage from './pages/NotFoundPage'
import PlayersPage from './pages/PlayersPage'
import TeamDetailsPage from './pages/TeamDetailsPage'
import TeamsPage from './pages/TeamsPage'
import type { MatchResponse } from './types/match'
import type { TeamResponse } from './types/team'

function currentPath() {
  return window.location.hash.slice(1) || '/'
}

function App() {
  const [path, setPath] = useState(currentPath)
  const [teams, setTeams] = useState<TeamResponse[]>([])
  const [matches, setMatches] = useState<MatchResponse[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [connected, setConnected] = useState(true)
  const [error, setError] = useState('')

  const navigate = useCallback((nextPath: string) => {
    const normalized = nextPath.startsWith('/') ? nextPath : `/${nextPath}`
    if (currentPath() === normalized) {
      setPath(normalized)
      return
    }
    window.location.hash = normalized
  }, [])
  const refresh = useCallback(async () => {
    try {
      const [teamList, matchList] = await Promise.all([teamsApi.getTeams({ limit: 100 }), matchesApi.getMatches({ limit: 100 })])
      setTeams(teamList)
      setMatches(matchList)
      setConnected(true)
      setError('')
    } catch (cause) {
      setConnected(false)
      setError(cause instanceof Error ? cause.message : 'Could not connect to the API.')
    } finally { setLoading(false) }
  }, [])

  useEffect(() => {
    const onRouteChange = () => { setPath(currentPath()); setError('') }
    window.addEventListener('hashchange', onRouteChange)
    void refresh()
    return () => window.removeEventListener('hashchange', onRouteChange)
  }, [refresh])

  const route = useMemo(() => resolveRoute(path), [path])
  const titles = { dashboard: 'Dashboard', teams: 'Teams', team: 'Team profile', players: 'Players', matches: 'Matches', createMatch: 'New match', match: 'Match details', notFound: 'Page not found' }
  const title = titles[route.name]

  return <div className="app-shell">
    <Sidebar path={path} navigate={navigate} matchCount={matches.length} connected={connected} />
    <main className="main-area">
      <Navbar title={title} search={search} onSearch={setSearch} onMenu={() => navigate('/matches')} />
      <div className="page-content">
        {error && <div className="alert" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss">×</button></div>}
        {loading ? <div className="loading"><span className="spinner" /> Loading MatchMind data...</div> : <>
          {route.name === 'dashboard' && <DashboardPage teams={teams} matches={matches} navigate={navigate} />}
          {route.name === 'teams' && <TeamsPage teams={teams} matches={matches} navigate={navigate} onRefresh={refresh} />}
          {route.name === 'team' && <TeamDetailsPage teamId={route.id} teams={teams} matches={matches} navigate={navigate} onRefresh={refresh} />}
          {route.name === 'players' && <PlayersPage teams={teams} />}
          {route.name === 'matches' && <MatchesPage matches={matches} teams={teams} search={search} navigate={navigate} />}
          {route.name === 'createMatch' && <CreateMatchPage teams={teams} navigate={navigate} />}
          {route.name === 'match' && <MatchDetailsPage key={route.id} matchId={route.id} teams={teams} navigate={navigate} onRefresh={refresh} />}
          {route.name === 'notFound' && <NotFoundPage navigate={navigate} />}
        </>}
      </div>
    </main>
  </div>
}

type Route = { name: 'dashboard' | 'teams' | 'players' | 'matches' | 'createMatch' | 'team' | 'match' | 'notFound'; id: string }

function resolveRoute(path: string): Route {
  if (path === '/') return { name: 'dashboard', id: '' }
  if (path === '/teams') return { name: 'teams', id: '' }
  if (path === '/players') return { name: 'players', id: '' }
  if (path === '/matches') return { name: 'matches', id: '' }
  if (path === '/matches/new') return { name: 'createMatch', id: '' }
  const team = path.match(/^\/teams\/([^/]+)$/)
  if (team) return { name: 'team', id: decodeURIComponent(team[1]) }
  const match = path.match(/^\/matches\/([^/]+)$/)
  if (match) return { name: 'match', id: decodeURIComponent(match[1]) }
  return { name: 'notFound', id: '' }
}

export default App
