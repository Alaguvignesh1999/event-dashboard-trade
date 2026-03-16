import { HeatmapChart } from "@/components/heatmap-chart";
import { PathChart } from "@/components/path-chart";
import { PresetShowcase } from "@/components/preset-showcase";
import { getHeatmap, getMetadata, getOverview, getPaths, getPresets, slugifyPreset } from "@/lib/data";

export default async function HomePage() {
  const [metadata, overview, presets] = await Promise.all([
    getMetadata(),
    getOverview(),
    getPresets(),
  ]);
  const defaultSlug = slugifyPreset(metadata.defaultPreset);
  const [heatmap, paths] = await Promise.all([getHeatmap(defaultSlug), getPaths(defaultSlug)]);

  return (
    <>
      <section className="hero-grid">
        <div className="hero-card panel">
          <span className="eyebrow">Deployable Macro Research</span>
          <h1>Event intelligence with a premium dark-mode control room feel.</h1>
          <p>
            This web build turns the notebook workflow into a snapshot-driven dashboard for
            historical event comparison, analogue ranking, and cross-asset trade framing.
          </p>
          <div className="metric-strip">
            {overview.cards.map((card) => (
              <div key={card.label} className="metric-tile">
                <div className="metric-label">{card.label}</div>
                <div className="metric-value mono">{card.value}</div>
                <div className="metric-detail">{card.detail}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel panel-card">
          <div className="section-head">
            <div>
              <span className="eyebrow">Run Health</span>
              <h2>Snapshot status</h2>
            </div>
          </div>
          <table className="table">
            <tbody>
              <tr>
                <th>Generated</th>
                <td className="mono">{metadata.generatedAt}</td>
              </tr>
              <tr>
                <th>Default preset</th>
                <td>{metadata.defaultPreset}</td>
              </tr>
              <tr>
                <th>FRED requested</th>
                <td className="mono">{metadata.fred.requested}</td>
              </tr>
              <tr>
                <th>FRED loaded</th>
                <td className="mono positive">{metadata.fred.loaded.length}</td>
              </tr>
              <tr>
                <th>Skipped without key</th>
                <td className="mono">{metadata.fred.skippedNoKey.length}</td>
              </tr>
              <tr>
                <th>Provider failures</th>
                <td className="mono negative">{metadata.fred.failedProvider.length}</td>
              </tr>
              <tr>
                <th>Data window</th>
                <td className="mono">
                  {metadata.startDate} to {metadata.endDate}
                </td>
              </tr>
            </tbody>
          </table>
          <p className="footer-note">
            The build remains usable without a FRED key; FRED-backed assets are marked as skipped
            instead of breaking the app.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="section-head">
          <div>
            <span className="eyebrow">Flagship Preset</span>
            <h2>{metadata.defaultPreset}</h2>
            <p>Average cross-asset response and normalized path profile for the default deployment view.</p>
          </div>
        </div>
        <div className="grid-two">
          <HeatmapChart payload={heatmap} />
          <PathChart payload={paths} />
        </div>
      </section>

      <section className="section">
        <div className="section-head">
          <div>
            <span className="eyebrow">Preset Stack</span>
            <h2>Research modes</h2>
            <p>Each preset keeps the source event taxonomy but presents it in a cleaner deployable shell.</p>
          </div>
        </div>
        <PresetShowcase presets={presets} />
      </section>

      <section className="section grid-two">
        <div className="panel panel-card">
          <div className="section-head">
            <div>
              <span className="eyebrow">Families</span>
              <h2>Event mix</h2>
            </div>
          </div>
          <div className="family-list">
            {overview.families.map((family) => (
              <div key={family.family} className="family-card">
                <div className="metric-label">{family.family}</div>
                <div className="metric-value mono">{family.count}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel panel-card">
          <div className="section-head">
            <div>
              <span className="eyebrow">Recent Events</span>
              <h2>Newest entries</h2>
            </div>
          </div>
          <div className="event-list">
            {overview.recentEvents.map((event) => (
              <div key={`${event.name}-${event.date}`} className="event-card">
                <div className="metric-label">{event.family}</div>
                <h3>{event.name}</h3>
                <p className="muted">{event.subtype || "Core event"}</p>
                <div className="event-meta">
                  <span className="chip mono">{event.date}</span>
                  <span className="chip">{event.region}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
