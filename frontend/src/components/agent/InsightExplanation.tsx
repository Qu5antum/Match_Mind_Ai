import type { GeneratedInsightExplanation } from '../../types/agent'

export default function InsightExplanation({ explanation }: { explanation: GeneratedInsightExplanation | null }) {
  if (!explanation) return null
  return <section className="panel agent-result"><div className="eyebrow">MATCHMIND AI EXPLANATION</div><h3>Why it matters</h3><p>{explanation.explanation}</p><p><b>Significance:</b> {explanation.significance}</p>
    {!!explanation.evidence_summary.length && <><h4>Evidence</h4><ul>{explanation.evidence_summary.map((fact) => <li key={fact}>{fact}</li>)}</ul></>}
    {!!explanation.limitations.length && <p className="agent-limitations">Limitations: {explanation.limitations.join(' ')}</p>}
  </section>
}
