import PageContainer from '../components/layout/PageContainer'

export default function NotFoundPage({ navigate }: { navigate: (path: string) => void }) {
  return <PageContainer eyebrow="404" title="Page not found" description="This address doesn't seem to belong to MatchMind.">
    <section className="panel empty-state"><span>⌁</span><h3>We lost possession</h3><p>Head back to the dashboard or browse your matches.</p><div className="form-actions"><button className="button primary" onClick={() => navigate('/')}>Dashboard</button><button className="button secondary" onClick={() => navigate('/matches')}>Matches</button></div></section>
  </PageContainer>
}
