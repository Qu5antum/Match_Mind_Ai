import type { MatchAnalyticsResponse } from '../../types/analytic'

function Metric({ label, home, away, suffix = '' }: { label: string; home: number; away: number; suffix?: string }) {
  const total = Math.max(home + away, 1)
  return <div className="metric"><div><b>{home}{suffix}</b><span>{label}</span><b>{away}{suffix}</b></div><div className="metric-bar"><i style={{ width: `${Math.max(3, home / total * 100)}%` }} /><i style={{ width: `${Math.max(3, away / total * 100)}%` }} /></div></div>
}

export default function MatchStats({ analytics }: { analytics: MatchAnalyticsResponse | null }) {
  if (!analytics) return <p className="placeholder">Match statistics will appear when analytics are available.</p>
  const home = analytics.teams.home.statistics
  const away = analytics.teams.away.statistics
  return <div className="metrics">
    <Metric label="Shots" home={home.shots} away={away.shots} />
    <Metric label="Shots on target" home={home.shots_on_target} away={away.shots_on_target} />
    <Metric label="Pass accuracy" home={home.pass_accuracy_percent ?? 0} away={away.pass_accuracy_percent ?? 0} suffix="%" />
    <Metric label="Tackles" home={home.tackles} away={away.tackles} />
    <Metric label="Corners" home={home.corners} away={away.corners} />
  </div>
}
