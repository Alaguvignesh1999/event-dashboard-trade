import { promises as fs } from "fs";
import path from "path";

import type {
  AnaloguesPayload,
  EventRecord,
  HeatmapPayload,
  Metadata,
  OverviewPayload,
  PathsPayload,
  PresetSummary,
  TradeIdeasPayload,
} from "@/lib/types";

const DATA_DIR = path.join(process.cwd(), "public", "data");

async function readJson<T>(...parts: string[]): Promise<T> {
  const filePath = path.join(DATA_DIR, ...parts);
  const raw = await fs.readFile(filePath, "utf8");
  return JSON.parse(raw) as T;
}

export function slugifyPreset(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

export async function getMetadata() {
  return readJson<Metadata>("metadata.json");
}

export async function getPresets() {
  return readJson<PresetSummary[]>("presets.json");
}

export async function getEvents() {
  return readJson<EventRecord[]>("events.json");
}

export async function getOverview() {
  return readJson<OverviewPayload>("overview.json");
}

export async function getHeatmap(slug: string) {
  return readJson<HeatmapPayload>("heatmaps", `${slug}.json`);
}

export async function getPaths(slug: string) {
  return readJson<PathsPayload>("paths", `${slug}.json`);
}

export async function getAnalogues(slug: string) {
  return readJson<AnaloguesPayload>("analogues", `${slug}.json`);
}

export async function getTradeIdeas(slug: string) {
  return readJson<TradeIdeasPayload>("trade-ideas", `${slug}.json`);
}
