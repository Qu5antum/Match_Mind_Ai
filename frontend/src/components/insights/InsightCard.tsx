import type { MatchInsightResponse } from '../../types/match_insight'

export default function InsightCard({ insight, onExplain }: { insight: MatchInsightResponse; onExplain?: (insight: MatchInsightResponse) => void }) {
  return <article className="panel insight-card">
    <div className="insight-card-top"><span className={`status ${insight.importance}`}>{insight.importance}</span><span className="insight-minute">{insight.minute == null ? '' : `${insight.minute}'`}</span></div>
    <h3>{insight.title}</h3><p>{insight.content}</p>
    {onExplain && <button className="text-link" onClick={() => onExplain(insight)}>Explain insight ↗</button>}
  </article>
}
