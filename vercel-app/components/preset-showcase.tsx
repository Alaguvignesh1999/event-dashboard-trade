import Link from "next/link";

import type { PresetSummary } from "@/lib/types";

export function PresetShowcase({ presets }: { presets: PresetSummary[] }) {
  return (
    <div className="preset-list">
      {presets.map((preset) => (
        <div key={preset.slug} className="preset-card panel">
          <span className="eyebrow">{preset.triggerAsset}</span>
          <h3>{preset.name}</h3>
          <p className="muted">{preset.highlight}</p>
          <div className="preset-meta">
            <span className="chip mono">{preset.eventCount} events</span>
            <span className="chip mono">{preset.assetCount} assets</span>
            <span className="chip mono">{preset.lastEventDate}</span>
          </div>
          <p className="footer-note">{preset.signal}</p>
          <div className="preset-meta">
            <Link href="/explore" className="chip accent">
              Open preset
            </Link>
            <Link href="/trade-ideas" className="chip">
              View ideas
            </Link>
          </div>
        </div>
      ))}
    </div>
  );
}
