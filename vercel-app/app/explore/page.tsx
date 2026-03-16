import { HeatmapChart } from "@/components/heatmap-chart";
import { PathChart } from "@/components/path-chart";
import { getHeatmap, getPaths, getPresets } from "@/lib/data";

export default async function ExplorePage() {
  const presets = await getPresets();
  const selected = presets[0];
  const [heatmap, paths] = await Promise.all([
    getHeatmap(selected.slug),
    getPaths(selected.slug),
  ]);

  return (
    <>
      <section className="page-heading">
        <span className="eyebrow">Explore</span>
        <h1>Preset exploration workspace.</h1>
        <p>
          V1 is snapshot-based: you can browse the preset library with clean, stable outputs that
          are easy to deploy and easy to explain.
        </p>
      </section>

      <section className="section">
        <div className="preset-list">
          {presets.map((preset) => (
            <div key={preset.slug} className="preset-card panel">
              <div className="metric-label">{preset.triggerAsset}</div>
              <h3>{preset.name}</h3>
              <p className="muted">{preset.highlight}</p>
              <div className="preset-meta">
                <span className="chip mono">{preset.eventCount} events</span>
                <span className="chip mono">{preset.lastEventDate}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="section grid-two">
        <div>
          <div className="section-head">
            <div>
              <span className="eyebrow">Heatmap</span>
              <h2>{selected.name}</h2>
              <p>Average response by horizon for the deployable asset set.</p>
            </div>
          </div>
          <HeatmapChart payload={heatmap} />
        </div>
        <div>
          <div className="section-head">
            <div>
              <span className="eyebrow">Path View</span>
              <h2>Normalized reactions</h2>
              <p>Mean event path from fifteen sessions before to thirty sessions after.</p>
            </div>
          </div>
          <PathChart payload={paths} />
        </div>
      </section>
    </>
  );
}
