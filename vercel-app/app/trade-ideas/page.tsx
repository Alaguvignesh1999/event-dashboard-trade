import { getMetadata, getTradeIdeas, slugifyPreset } from "@/lib/data";

export default async function TradeIdeasPage() {
  const metadata = await getMetadata();
  const payload = await getTradeIdeas(slugifyPreset(metadata.defaultPreset));

  return (
    <>
      <section className="page-heading">
        <span className="eyebrow">Trade Ideas</span>
        <h1>Actionable framing for the current preset stack.</h1>
        <p>
          These are systematic ideas derived from the exported analogue and path summaries. They are
          meant to be discussion-ready, not black-box signals.
        </p>
      </section>

      <section className="section">
        <div className="idea-list">
          {payload.ideas.map((idea) => (
            <div key={idea.title} className="idea-card panel">
              <div className="metric-label">
                {idea.direction} · {idea.horizon}
              </div>
              <h3>{idea.title}</h3>
              <p className="muted">{idea.thesis}</p>
              <div className="idea-meta">
                <span className="chip mono">{idea.asset}</span>
                <span className="chip mono">{idea.conviction}</span>
                <span className="chip mono">{idea.expectedMove}</span>
              </div>
              <p className="footer-note">
                <span className="accent">Support:</span> {idea.support}
              </p>
              <p className="footer-note">
                <span className="negative">Risk:</span> {idea.risk}
              </p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
