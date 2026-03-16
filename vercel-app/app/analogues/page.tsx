import { getAnalogues, getMetadata, slugifyPreset } from "@/lib/data";

export default async function AnaloguesPage() {
  const metadata = await getMetadata();
  const analogues = await getAnalogues(slugifyPreset(metadata.defaultPreset));

  return (
    <>
      <section className="page-heading">
        <span className="eyebrow">Analogues</span>
        <h1>Similarity ranking with readable reasoning.</h1>
        <p>
          The newest event in each preset becomes the anchor, then prior events are ranked using
          family, tag, and recency-aware heuristics.
        </p>
      </section>

      <section className="section">
        <div className="panel panel-card">
          <div className="section-head">
            <div>
              <span className="eyebrow">Target Event</span>
              <h2>{analogues.targetEvent.name}</h2>
              <p>
                {analogues.targetEvent.date} · {analogues.targetEvent.family}
              </p>
            </div>
          </div>
          <div className="preset-meta">
            {analogues.targetEvent.tags.map((tag) => (
              <span key={tag} className="chip mono">
                {tag}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="analogue-list">
          {analogues.rankings.map((row) => (
            <div key={`${row.name}-${row.date}`} className="analogue-card panel">
              <div className="metric-label">Similarity score</div>
              <h3>
                {row.name} <span className="accent mono">{row.score.toFixed(2)}</span>
              </h3>
              <p className="muted">{row.whyItMatches}</p>
              <div className="analogue-meta">
                <span className="chip mono">{row.date}</span>
                <span className="chip">{row.family}</span>
                <span className={`chip mono ${(row.forward5d ?? 0) >= 0 ? "positive" : "negative"}`}>
                  5D {row.forward5d === null ? "n/a" : `${row.forward5d.toFixed(2)}%`}
                </span>
                <span className={`chip mono ${(row.forward20d ?? 0) >= 0 ? "positive" : "negative"}`}>
                  20D {row.forward20d === null ? "n/a" : `${row.forward20d.toFixed(2)}%`}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
