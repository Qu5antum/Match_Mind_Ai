import type { MatchInsightResponse } from '../../types/match_insight'
import InsightCard from './InsightCard'

export default function InsightList({ insights, onExplain }: { insights: MatchInsightResponse[]; onExplain?: (insight: MatchInsightResponse) => void }) {
  if (!insights.length) return <div className="panel empty-state"><span>✳</span><h3>No insights yet</h3><p>Generate an AI analysis for this match.</p></div>
  return <div className="insights-list">{insights.map((insight) => <InsightCard key={insight.id} insight={insight} onExplain={onExplain} />)}</div>
}
