export type FredStatus = {
  requested: number;
  loaded: string[];
  skippedNoKey: string[];
  failedProvider: string[];
};

export type AssetRecord = {
  key: string;
  label: string;
  displayLabel: string;
  source: "yf" | "fred";
  symbol: string;
  category: string;
  coverage: number;
};

export type PresetSummary = {
  name: string;
  slug: string;
  triggerAsset: string;
  eventCount: number;
  lastEventName: string;
  lastEventDate: string;
  highlight: string;
  signal: string;
  assetCount: number;
  similarityPool: string[];
};

export type Metadata = {
  generatedAt: string;
  defaultPreset: string;
  presetCount: number;
  eventCount: number;
  startDate: string;
  endDate: string;
  fred: FredStatus;
  assets: AssetRecord[];
};

export type EventRecord = {
  name: string;
  date: string;
  family: string;
  subtype: string;
  region: string;
  tags: string[];
  notes: string;
  presets: string[];
};

export type OverviewCard = {
  label: string;
  value: string;
  detail: string;
};

export type OverviewPayload = {
  cards: OverviewCard[];
  families: { family: string; count: number }[];
  recentEvents: EventRecord[];
};

export type HeatmapPayload = {
  preset: string;
  presetSlug: string;
  assets: string[];
  horizons: string[];
  values: number[][];
  coverageNotes: string[];
};

export type PathSeries = {
  asset: string;
  displayLabel: string;
  latestSpot: number | null;
  latestDate: string | null;
  coverage: number;
  values: number[];
};

export type PathsPayload = {
  preset: string;
  presetSlug: string;
  days: number[];
  series: PathSeries[];
};

export type AnalogueRecord = {
  name: string;
  date: string;
  family: string;
  score: number;
  whyItMatches: string;
  forward5d: number | null;
  forward20d: number | null;
};

export type AnaloguesPayload = {
  preset: string;
  presetSlug: string;
  targetEvent: {
    name: string;
    date: string;
    family: string;
    tags: string[];
  };
  rankings: AnalogueRecord[];
};

export type TradeIdea = {
  title: string;
  asset: string;
  direction: "Long" | "Short" | "Relative Value";
  horizon: string;
  conviction: string;
  expectedMove: string;
  thesis: string;
  risk: string;
  support: string;
};

export type TradeIdeasPayload = {
  preset: string;
  presetSlug: string;
  generatedAt: string;
  ideas: TradeIdea[];
};
