import { getMetadata } from "@/lib/data";

export default async function MethodologyPage() {
  const metadata = await getMetadata();

  return (
    <>
      <section className="page-heading">
        <span className="eyebrow">Methodology</span>
        <h1>Transparent, snapshot-driven, and deployment-friendly.</h1>
        <p>
          The production web app is intentionally separated from the notebook runtime. That keeps
          Vercel deployment predictable and gives you a cleaner handoff surface.
        </p>
      </section>

      <section className="section method-grid">
        <div className="method-card panel">
          <div className="metric-label">Sources</div>
          <h3>Notebook-aligned data inputs</h3>
          <p className="muted">
            The app reuses the existing `events.yaml` taxonomy and `universal_preset_loader.py`
            preset definitions. Market history comes from a focused subset of yfinance and FRED.
          </p>
        </div>
        <div className="method-card panel">
          <div className="metric-label">Secrets</div>
          <h3>Environment variable only</h3>
          <p className="muted">
            `FRED_API_KEY` is read at build time. Without it, the exporter still succeeds and marks
            FRED-only series as skipped. With it, the build attempts the full credit and breakeven set.
          </p>
        </div>
        <div className="method-card panel">
          <div className="metric-label">Current snapshot</div>
          <h3>{metadata.generatedAt}</h3>
          <p className="muted">
            {metadata.fred.loaded.length} FRED series loaded, {metadata.fred.failedProvider.length} provider
            issues, {metadata.fred.skippedNoKey.length} skipped without a key.
          </p>
        </div>
      </section>
    </>
  );
}
