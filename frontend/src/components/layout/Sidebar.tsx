export type AppRoute = '/' | '/teams' | '/players' | '/matches' | '/insights'

const links: { path: AppRoute; label: string; icon: string }[] = [
  { path: '/', label: 'Dashboard', icon: '▦' },
  { path: '/matches', label: 'Matches', icon: '◉' },
  { path: '/teams', label: 'Teams', icon: '♙' },
  { path: '/players', label: 'Players', icon: '♟' },
  { path: '/insights', label: 'AI Insights', icon: '✳' },
]

export default function Sidebar({ path, navigate, matchCount, connected }: {
  path: string
  navigate: (path: string) => void
  matchCount: number
  connected: boolean
}) {
  return <aside className="sidebar">
    <button className="brand" onClick={() => navigate('/')}><span className="brand-mark">◉</span><span>matchmind<span className="brand-ai">AI</span></span></button>
    <div className="nav-caption">WORKSPACE</div>
    <nav aria-label="Main navigation">
      {links.map((link) => {
        const active = link.path === '/' ? path === '/' : path.startsWith(link.path)
        return <button key={link.path} className={`nav-item ${active ? 'active' : ''}`} onClick={() => navigate(link.path)}>
          <span className="nav-icon">{link.icon}</span>{link.label}
          {link.path === '/matches' && <span className="nav-count">{matchCount}</span>}
        </button>
      })}
    </nav>
    <div className="sidebar-footer"><span className={`connection-dot ${connected ? '' : 'offline'}`} />{connected ? 'Platform ready' : 'Connection issue'}
      <div className="profile"><span className="avatar">MM</span><span><b>MatchMind Studio</b><small>Analyst dashboard</small></span><i>···</i></div>
    </div>
  </aside>
}
