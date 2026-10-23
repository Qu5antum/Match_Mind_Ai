export default function Navbar({ title, search, onSearch, onMenu }: {
  title: string
  search: string
  onSearch: (value: string) => void
  onMenu: () => void
}) {
  return <header className="topbar">
    <div className="breadcrumbs">MatchMind <span>/</span> <b>{title}</b></div>
    <div className="topbar-right">
      <label className="search"><span>⌕</span><input placeholder="Search matches..." aria-label="Search matches" value={search} onChange={(event) => onSearch(event.target.value)} /></label>
      <span className="today">{new Intl.DateTimeFormat('en-US', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date())}</span>
      <button className="mobile-nav" onClick={onMenu} aria-label="Open matches">☰</button>
    </div>
  </header>
}
