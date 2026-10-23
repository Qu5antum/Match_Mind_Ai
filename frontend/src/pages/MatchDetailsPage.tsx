import { useCallback, useEffect, useMemo, useState } from 'react'
import { agentApi } from '../api/agent'
import { analyticsApi } from '../api/analytics'
import { insightsApi } from '../api/insights'
import { matchesApi } from '../api/matches'
import { matchEventService } from '../api/match_event_api'
import MatchEvents from '../components/matches/MatchEvents'
import MatchScore from '../components/matches/MatchScore'
import MatchStats from '../components/matches/MatchStats'
import InsightExplanation from '../components/agent/InsightExplanation'
import MatchChat from '../components/agent/MatchChat'
import InsightList from '../components/insights/InsightList'
import PageContainer from '../components/layout/PageContainer'
import type { GeneratedInsightExplanation, MatchQuestionResponse } from '../types/agent'
import type { MatchAnalyticsResponse } from '../types/analytic'
import type { MatchEventResponse } from '../types/match_event'
import type { DetailedMatchResponse, MatchResponse } from '../types/match'
import type { MatchInsightResponse } from '../types/match_insight'
import type { TeamResponse } from '../types/team'

export default function MatchDetailsPage({ matchId, teams, navigate, onRefresh }: {
  matchId: string
  teams: TeamResponse[]
  navigate: (path: string) => void
  onRefresh: () => Promise<void>
}) {
  const [match, setMatch] = useState<DetailedMatchResponse | MatchResponse | null>(null)
  const [events, setEvents] = useState<MatchEventResponse[]>([])
  const [analytics, setAnalytics] = useState<MatchAnalyticsResponse | null>(null)
  const [insights, setInsights] = useState<MatchInsightResponse[]>([])
  const [summary, setSummary] = useState('')
  const [answer, setAnswer] = useState<MatchQuestionResponse | null>(null)
  const [explanation, setExplanation] = useState<GeneratedInsightExplanation | null>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const teamMap = useMemo(() => new Map(teams.map((team) => [team.id, team])), [teams])

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const detail = await matchesApi.getMatchDetail(matchId)
      setMatch(detail)
      const results = await Promise.allSettled([
        matchEventService.getMatchEvents(matchId, { limit: 500 }),
        analyticsApi.getMatchAnalytics(matchId),
        insightsApi.getMatchInsights(matchId, { limit: 100 }),
      ])
      if (results[0].status === 'fulfilled') setEvents(results[0].value)
      if (results[1].status === 'fulfilled') setAnalytics(results[1].value)
      if (results[2].status === 'fulfilled') setInsights(results[2].value)
      const failed = results.filter((result) => result.status === 'rejected')
      if (failed.length) setError('Some match data is currently unavailable. Check the match status or try refreshing.')
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not load match.')
    } finally { setLoading(false) }
  }, [matchId])
  useEffect(() => { void load() }, [load])

  const act = async (action: 'simulate' | 'play' | 'pause' | 'finish') => {
    if (!match) return
    setBusy(true); setError('')
    try {
      if (action === 'simulate') await matchesApi.simulateMatch(match.id)
      else if (action === 'play') await matchesApi.playMatch(match.id)
      else if (action === 'pause') await matchesApi.pauseMatch(match.id)
      else await matchesApi.finishMatch(match.id)
      await Promise.all([load(), onRefresh()])
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not perform this match action.') }
    finally { setBusy(false) }
  }
  const generateInsights = async () => {
    setBusy(true); setError('')
    try { await insightsApi.generateMatchInsights(matchId, { language: 'en', audience: 'coach' }); setInsights(await insightsApi.getMatchInsights(matchId, { limit: 100 })) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not generate AI insights.') }
    finally { setBusy(false) }
  }
  const requestSummary = async () => {
    setBusy(true); setError('')
    try { setSummary((await agentApi.summarizeMatch(matchId, { language: 'en' })).summary) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not generate a match summary.') }
    finally { setBusy(false) }
  }
  const ask = async (question: string) => {
    setBusy(true); setError('')
    try { setAnswer(await agentApi.askAboutMatch(matchId, { question, language: 'en' })) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not get an AI answer.') }
    finally { setBusy(false) }
  }
  const explain = async (insight: MatchInsightResponse) => {
    setBusy(true); setExplanation(null); setError('')
    try { setExplanation(await agentApi.explainInsight(insight.id, { language: 'en', audience: 'coach' })) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not explain this insight.') }
    finally { setBusy(false) }
  }
  const tacticalAnalysis = async () => {
    setBusy(true); setError('')
    try {
      const analysis = await agentApi.generateTacticalAnalysis(matchId, { language: 'en' })
      setSummary([analysis.overview, ...analysis.tactical_observations].join('\n\n'))
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not generate tactical analysis.') }
    finally { setBusy(false) }
  }

  const home = match ? teamMap.get(match.home_team_id) : undefined
  const away = match ? teamMap.get(match.away_team_id) : undefined
  if (loading) return <div className="loading"><span className="spinner" /> Loading match...</div>
  if (!match) return <PageContainer title="Match not found"><div className="panel empty-state"><p>The match could not be found or the API is unavailable.</p><button className="button secondary" onClick={() => navigate('/matches')}>← All matches</button></div></PageContainer>

  return <PageContainer eyebrow="MATCH / DETAILS" title={`${home?.short_name ?? 'HOME'} vs ${away?.short_name ?? 'AWAY'}`}
    description="Score, match timeline, statistics, and AI analysis."
    action={<button className="button secondary" onClick={() => navigate('/matches')}>← All matches</button>}>
    {error && <div className="alert" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss">×</button></div>}
    <section className="panel match-detail-panel">
      <div className="detail-top"><span className={`status ${match.status}`}>{statusLabels[match.status] ?? match.status}</span><span>Seed {match.seed} · {new Intl.DateTimeFormat('en-US', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(match.created_at))}</span></div>
      <MatchScore match={match} home={home} away={away} />
      <div className="detail-actions">
        {match.status === 'created' && <button className="button primary" disabled={busy} onClick={() => void act('simulate')}>{busy ? 'Simulating...' : 'Run simulation'}</button>}
        {['ready', 'paused'].includes(match.status) && <button className="button primary" disabled={busy} onClick={() => void act('play')}>Resume match</button>}
        {match.status === 'playing' && <><button className="button secondary" disabled={busy} onClick={() => void act('pause')}>Pause</button><button className="button secondary" disabled={busy} onClick={() => void act('finish')}>Finish</button></>}
        <button className="button secondary" disabled={busy} onClick={() => void requestSummary()}>✳ AI summary</button>
        <button className="button secondary" disabled={busy} onClick={() => void tacticalAnalysis()}>Tactical analysis</button>
      </div>
    </section>
    {summary && <section className="panel summary-box"><b>✳ MATCHMIND AI ANALYSIS</b><p>{summary}</p></section>}
    <div className="detail-columns">
      <section className="panel detail-section"><div className="panel-heading"><div><h2>Statistics</h2><p>{analytics ? `${analytics.metadata.events_analyzed} events · algorithm ${analytics.metadata.algorithm_version}` : 'Match analytics'}</p></div></div><MatchStats analytics={analytics} /></section>
      <section className="panel detail-section"><div className="panel-heading"><div><h2>Timeline</h2><p>{events.length} events</p></div></div><MatchEvents events={events} teams={teamMap} /></section>
    </div>
    <div className="page-subsection-heading"><div><h2>AI insights</h2><p>Analysis and key moments from the match</p></div><button className="button secondary" disabled={busy} onClick={() => void generateInsights()}>{busy ? 'Generating...' : '✳ Generate insights'}</button></div>
    <InsightList insights={insights} onExplain={(insight) => void explain(insight)} />
    {busy && <p className="placeholder">AI is processing your request...</p>}
    <InsightExplanation explanation={explanation} />
    <MatchChat busy={busy} answer={answer} onAsk={ask} />
  </PageContainer>
}

const statusLabels: Record<string, string> = { created: 'Created', simulating: 'Simulating', ready: 'Ready', playing: 'Live', paused: 'Paused', finished: 'Finished', failed: 'Failed' }
