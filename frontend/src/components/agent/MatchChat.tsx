import { useState, type FormEvent } from 'react'
import type { MatchQuestionResponse } from '../../types/agent'

export default function MatchChat({ busy, answer, onAsk }: {
  busy: boolean
  answer: MatchQuestionResponse | null
  onAsk: (question: string) => Promise<void>
}) {
  const [question, setQuestion] = useState('')
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || busy) return
    void onAsk(trimmed)
    setQuestion('')
  }
  return <section className="panel chat-panel"><div className="eyebrow">MATCHMIND AI</div><h3>Ask about this match</h3>
    <form className="chat-form" onSubmit={submit}><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="For example: why did the home team win?" aria-label="Ask a question about the match" maxLength={500} /><button className="button primary" disabled={busy || !question.trim()}>{busy ? 'Thinking...' : 'Ask'}</button></form>
    {answer && <div className="chat-answer"><p>{answer.answer}</p>{!!answer.supporting_facts.length && <ul>{answer.supporting_facts.map((fact) => <li key={fact}>{fact}</li>)}</ul>}{!!answer.limitations.length && <small>{answer.limitations.join(' ')}</small>}</div>}
  </section>
}
