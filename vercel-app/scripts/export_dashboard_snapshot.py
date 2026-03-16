from __future__ import annotations

import json
import os
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yfinance as yf
import yaml


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA_DIR = ROOT / "public" / "data"
EVENTS_PATH = ROOT / "events.yaml"
WINDOW_PRE = 15
WINDOW_POST = 30
HORIZONS = [1, 5, 10, 20]
TODAY = pd.Timestamp.utcnow().normalize().tz_localize(None)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from universal_preset_loader import PRESET_CONFIGS, load_preset_pack


ASSETS: list[dict[str, str]] = [
    {"key": "Brent Futures", "symbol": "BZ=F", "source": "yf", "category": "Oil & Energy"},
    {"key": "WTI Crude (spot)", "symbol": "CL=F", "source": "yf", "category": "Oil & Energy"},
    {"key": "Gold", "symbol": "GC=F", "source": "yf", "category": "Precious Metals"},
    {"key": "DXY", "symbol": "DX-Y.NYB", "source": "yf", "category": "FX"},
    {"key": "S&P 500", "symbol": "^GSPC", "source": "yf", "category": "Equities"},
    {"key": "US 10Y Yield", "symbol": "^TNX", "source": "yf", "category": "Rates"},
    {"key": "VIX", "symbol": "^VIX", "source": "yf", "category": "Volatility"},
    {"key": "EURUSD", "symbol": "EURUSD=X", "source": "yf", "category": "FX"},
    {"key": "USDJPY", "symbol": "USDJPY=X", "source": "yf", "category": "FX"},
    {"key": "Copper", "symbol": "HG=F", "source": "yf", "category": "Metals"},
    {"key": "Shipping (BDRY)", "symbol": "BDRY", "source": "yf", "category": "Shipping"},
    {"key": "US 10Y Breakeven", "symbol": "T10YIE", "source": "fred", "category": "Rates"},
    {"key": "US 5Y Breakeven", "symbol": "T5YIE", "source": "fred", "category": "Rates"},
    {"key": "US 10Y Real Yield", "symbol": "DFII10", "source": "fred", "category": "Rates"},
    {"key": "US IG OAS", "symbol": "BAMLC0A0CM", "source": "fred", "category": "Credit"},
    {"key": "US BBB OAS", "symbol": "BAMLC0A4CBBB", "source": "fred", "category": "Credit"},
    {"key": "US HY OAS", "symbol": "BAMLH0A0HYM2", "source": "fred", "category": "Credit"},
    {"key": "Euro HY OAS", "symbol": "BAMLHE00EHY0EY", "source": "fred", "category": "Credit"},
]


@dataclass
class FredStatus:
    requested: int
    loaded: list[str]
    skippedNoKey: list[str]
    failedProvider: list[str]


def display_label(label: str) -> str:
    return "USDEUR" if label == "EURUSD" else label


def slugify(name: str) -> str:
    return "-".join(chunk for chunk in "".join(c.lower() if c.isalnum() else "-" for c in name).split("-") if chunk)


def ensure_directories() -> None:
    for folder in [
        PUBLIC_DATA_DIR,
        PUBLIC_DATA_DIR / "heatmaps",
        PUBLIC_DATA_DIR / "paths",
        PUBLIC_DATA_DIR / "analogues",
        PUBLIC_DATA_DIR / "trade-ideas",
    ]:
        folder.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_event_rows() -> list[dict[str, Any]]:
    raw = yaml.safe_load(EVENTS_PATH.read_text(encoding="utf-8")) or {}
    rows = raw.get("events") or []
    return [row for row in rows if row.get("name") and row.get("date")]


def fetch_yfinance_series(symbol: str, start: str, end: str) -> pd.Series:
    frame = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=True, threads=False)
    if frame is None or frame.empty:
        return pd.Series(dtype=float)
    if isinstance(frame.columns, pd.MultiIndex):
        close = frame["Close"].iloc[:, 0]
    else:
        close = frame["Close"] if "Close" in frame.columns else frame.iloc[:, 0]
    close.index = pd.to_datetime(close.index).tz_localize(None)
    return pd.to_numeric(close, errors="coerce").dropna()


def fetch_fred_series(series_id: str, start: str, api_key: str) -> pd.Series:
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
    }
    response = requests.get(url, params=params, timeout=45)
    response.raise_for_status()
    observations = response.json().get("observations") or []
    rows = []
    for obs in observations:
        value = obs.get("value")
        if value in {None, ".", ""}:
            continue
        try:
            rows.append((pd.Timestamp(obs["date"]), float(value)))
        except Exception:
            continue
    if not rows:
        return pd.Series(dtype=float)
    series = pd.Series({dt: val for dt, val in rows}).sort_index()
    series.index = pd.to_datetime(series.index).tz_localize(None)
    return series


def build_price_table(rows: list[dict[str, Any]], fred_key: str | None) -> tuple[pd.DataFrame, FredStatus]:
    first_date = min(pd.Timestamp(row["date"]) for row in rows)
    start = (first_date - pd.Timedelta(days=120)).strftime("%Y-%m-%d")
    end = (TODAY + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    data: dict[str, pd.Series] = {}
    fred_status = FredStatus(requested=0, loaded=[], skippedNoKey=[], failedProvider=[])

    for asset in ASSETS:
        label = asset["key"]
        if asset["source"] == "fred":
            fred_status.requested += 1
            if not fred_key:
                fred_status.skippedNoKey.append(label)
                continue
            try:
                series = fetch_fred_series(asset["symbol"], start, fred_key)
            except Exception:
                fred_status.failedProvider.append(label)
                continue
            if series.empty:
                fred_status.failedProvider.append(label)
                continue
            fred_status.loaded.append(label)
            data[label] = series
            continue

        try:
            series = fetch_yfinance_series(asset["symbol"], start, end)
        except Exception:
            continue
        if not series.empty:
            data[label] = series

    if not data:
        raise RuntimeError("No time series could be loaded for the dashboard snapshot export.")

    frame = pd.DataFrame(data).sort_index()
    return frame, fred_status


def get_anchor_index(series: pd.Series, event_date: str) -> int | None:
    clean = series.dropna()
    if clean.empty:
        return None
    event_ts = pd.Timestamp(event_date)
    pos = clean.index.searchsorted(event_ts)
    if pos >= len(clean.index):
        pos = len(clean.index) - 1
    if pos < len(clean.index) and clean.index[pos] < event_ts and pos + 1 < len(clean.index):
        pos += 1
    return int(pos)


def calc_forward_move(series: pd.Series, event_date: str, horizon: int) -> float | None:
    clean = series.dropna()
    anchor = get_anchor_index(clean, event_date)
    if anchor is None or anchor + horizon >= len(clean):
        return None
    base = clean.iloc[anchor]
    later = clean.iloc[anchor + horizon]
    if pd.isna(base) or base == 0 or pd.isna(later):
        return None
    return float((later / base - 1.0) * 100.0)


def calc_path(series: pd.Series, event_date: str) -> list[float | None] | None:
    clean = series.dropna()
    anchor = get_anchor_index(clean, event_date)
    if anchor is None:
        return None
    base = clean.iloc[anchor]
    if pd.isna(base) or base == 0:
        return None
    values: list[float | None] = []
    for offset in range(-WINDOW_PRE, WINDOW_POST + 1):
        idx = anchor + offset
        if idx < 0 or idx >= len(clean):
            values.append(None)
            continue
        point = clean.iloc[idx]
        if pd.isna(point):
            values.append(None)
            continue
        values.append(float((point / base - 1.0) * 100.0))
    return values


def mean_ignore_none(values: list[float | None]) -> float | None:
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return float(sum(clean) / len(clean))


def build_event_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["name"]): row for row in rows}


def score_analogue(target: dict[str, Any], candidate: dict[str, Any]) -> tuple[float, str]:
    target_tags = set(target.get("tags") or [])
    candidate_tags = set(candidate.get("tags") or [])
    overlap = len(target_tags.intersection(candidate_tags))
    union = len(target_tags.union(candidate_tags)) or 1
    tag_score = overlap / union
    family_score = 1.0 if target.get("family") == candidate.get("family") else 0.0
    region_score = 1.0 if target.get("region") == candidate.get("region") else 0.0
    date_gap = abs((pd.Timestamp(target["date"]) - pd.Timestamp(candidate["date"])).days)
    recency_score = max(0.0, 1.0 - (date_gap / 3650.0))
    score = 0.45 * family_score + 0.3 * tag_score + 0.15 * region_score + 0.1 * recency_score
    reasons = []
    if family_score:
        reasons.append("same family")
    if overlap:
        reasons.append(f"{overlap} shared tags")
    if region_score:
        reasons.append("same region")
    if not reasons:
        reasons.append("cross-theme analogue")
    return float(score), ", ".join(reasons)


def build_preset_payloads(frame: pd.DataFrame, rows: list[dict[str, Any]], fred_status: FredStatus) -> list[dict[str, Any]]:
    event_index = build_event_index(rows)
    presets_payload: list[dict[str, Any]] = []

    for preset_name, config in PRESET_CONFIGS.items():
        pack = load_preset_pack(str(EVENTS_PATH), preset_name)
        if not pack.events:
            continue
        preset_slug = slugify(preset_name)
        similarity_assets = [config["trigger_asset"], *config["sim_pool_base"]]
        ordered_assets = []
        for asset in similarity_assets:
            if asset not in ordered_assets:
                ordered_assets.append(asset)

        heatmap_assets = [asset for asset in ordered_assets if asset in frame.columns][:8]
        heatmap_values: list[list[float]] = []
        coverage_notes: list[str] = []
        for asset in heatmap_assets:
            series = frame[asset]
            horizon_values = []
            usable_events = 0
            for horizon in HORIZONS:
                moves = [calc_forward_move(series, event_date, horizon) for _, event_date in pack.events]
                usable = [move for move in moves if move is not None]
                if usable:
                    usable_events = max(usable_events, len(usable))
                horizon_values.append(round(mean_ignore_none(moves) or 0.0, 2))
            heatmap_values.append(horizon_values)
            note = f"{display_label(asset)}: {usable_events}/{len(pack.events)} events with usable paths"
            if asset in fred_status.skippedNoKey:
                note += " - FRED disabled"
            elif asset in fred_status.failedProvider:
                note += " - provider unavailable"
            elif usable_events < max(3, len(pack.events) // 3):
                note += " - structurally limited coverage"
            coverage_notes.append(note)

        write_json(
            PUBLIC_DATA_DIR / "heatmaps" / f"{preset_slug}.json",
            {
                "preset": preset_name,
                "presetSlug": preset_slug,
                "assets": [display_label(asset) for asset in heatmap_assets],
                "horizons": [f"{horizon}D" for horizon in HORIZONS],
                "values": heatmap_values,
                "coverageNotes": coverage_notes,
            },
        )

        days = list(range(-WINDOW_PRE, WINDOW_POST + 1))
        path_assets = heatmap_assets[:6]
        path_series = []
        for asset in path_assets:
            event_paths = [calc_path(frame[asset], event_date) for _, event_date in pack.events]
            averaged = []
            for idx in range(len(days)):
                averaged.append(
                    round(
                        mean_ignore_none(
                            [event_path[idx] for event_path in event_paths if event_path is not None]
                        )
                        or 0.0,
                        2,
                    )
                )
            clean_series = frame[asset].dropna()
            path_series.append(
                {
                    "asset": asset,
                    "displayLabel": display_label(asset),
                    "latestSpot": round(float(clean_series.iloc[-1]), 4) if not clean_series.empty else None,
                    "latestDate": clean_series.index[-1].strftime("%Y-%m-%d") if not clean_series.empty else None,
                    "coverage": sum(1 for event_path in event_paths if event_path is not None),
                    "values": averaged,
                }
            )

        write_json(
            PUBLIC_DATA_DIR / "paths" / f"{preset_slug}.json",
            {
                "preset": preset_name,
                "presetSlug": preset_slug,
                "days": days,
                "series": path_series,
            },
        )

        target_name, target_date = pack.events[-1]
        target_row = event_index[target_name]
        trigger_asset = config["trigger_asset"]
        rankings = []
        for candidate_name, candidate_date in pack.events[:-1]:
            candidate_row = event_index[candidate_name]
            score, why = score_analogue(target_row, candidate_row)
            rankings.append(
                {
                    "name": candidate_name,
                    "date": candidate_date,
                    "family": candidate_row.get("family") or "",
                    "score": round(score, 3),
                    "whyItMatches": why,
                    "forward5d": round(calc_forward_move(frame[trigger_asset], candidate_date, 5), 2)
                    if trigger_asset in frame.columns and calc_forward_move(frame[trigger_asset], candidate_date, 5) is not None
                    else None,
                    "forward20d": round(calc_forward_move(frame[trigger_asset], candidate_date, 20), 2)
                    if trigger_asset in frame.columns and calc_forward_move(frame[trigger_asset], candidate_date, 20) is not None
                    else None,
                }
            )
        rankings = sorted(rankings, key=lambda item: item["score"], reverse=True)[:8]

        write_json(
            PUBLIC_DATA_DIR / "analogues" / f"{preset_slug}.json",
            {
                "preset": preset_name,
                "presetSlug": preset_slug,
                "targetEvent": {
                    "name": target_name,
                    "date": target_date,
                    "family": target_row.get("family") or "",
                    "tags": list(target_row.get("tags") or []),
                },
                "rankings": rankings,
            },
        )

        ideas = []
        top_support = ", ".join(row["name"] for row in rankings[:2]) if rankings else "historical cluster support"
        for asset, horizon_values in zip(heatmap_assets[:3], heatmap_values[:3]):
            move_5d = horizon_values[1] if len(horizon_values) > 1 else 0.0
            direction = "Long" if move_5d >= 0 else "Short"
            conviction = "High" if abs(move_5d) >= 4 else "Medium" if abs(move_5d) >= 2 else "Tactical"
            ideas.append(
                {
                    "title": f"{direction} {display_label(asset)} around {preset_name}",
                    "asset": display_label(asset),
                    "direction": direction,
                    "horizon": "5D to 20D",
                    "conviction": conviction,
                    "expectedMove": f"{move_5d:+.2f}% avg 5D",
                    "thesis": f"Historical average paths show {display_label(asset)} leaning {direction.lower()} after {preset_name} events.",
                    "risk": "Fast de-escalation, data revisions, and cross-asset mean reversion can overwhelm the analogue base case.",
                    "support": top_support,
                }
            )

        if len(heatmap_assets) >= 2:
            ideas.append(
                {
                    "title": f"Relative value: {display_label(heatmap_assets[0])} vs {display_label(heatmap_assets[1])}",
                    "asset": f"{display_label(heatmap_assets[0])} / {display_label(heatmap_assets[1])}",
                    "direction": "Relative Value",
                    "horizon": "10D",
                    "conviction": "Tactical",
                    "expectedMove": "Use dispersion between the top two path profiles",
                    "thesis": "The strongest preset-level asset and the second-strongest asset diverge consistently enough to frame a relative trade.",
                    "risk": "Spread compression can happen quickly if the trigger reprices before cross-asset confirmation arrives.",
                    "support": top_support,
                }
            )

        write_json(
            PUBLIC_DATA_DIR / "trade-ideas" / f"{preset_slug}.json",
            {
                "preset": preset_name,
                "presetSlug": preset_slug,
                    "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "ideas": ideas,
            },
        )

        strongest_asset = None
        strongest_move = None
        for asset, horizon_values in zip(heatmap_assets, heatmap_values):
            move = abs(horizon_values[1]) if len(horizon_values) > 1 else 0.0
            if strongest_move is None or move > strongest_move:
                strongest_move = move
                strongest_asset = asset

        presets_payload.append(
            {
                "name": preset_name,
                "slug": preset_slug,
                "triggerAsset": config["trigger_asset"],
                "eventCount": len(pack.events),
                "lastEventName": target_name,
                "lastEventDate": target_date,
                "highlight": f"{len(pack.events)} events anchored by {config['trigger_asset']} with {len(heatmap_assets)} deployable assets.",
                "signal": f"Strongest 5D average reaction: {display_label(strongest_asset or config['trigger_asset'])}.",
                "assetCount": len(heatmap_assets),
                "similarityPool": [display_label(asset) for asset in ordered_assets],
            }
        )

    return presets_payload


def main() -> None:
    ensure_directories()
    rows = load_event_rows()
    fred_key = (os.getenv("FRED_API_KEY") or "").strip() or None
    frame, fred_status = build_price_table(rows, fred_key)

    presets_payload = build_preset_payloads(frame, rows, fred_status)
    default_preset = "Middle East Conflict" if any(
        payload["name"] == "Middle East Conflict" for payload in presets_payload
    ) else presets_payload[0]["name"]

    preset_membership = {
        preset_name: {name for name, _ in load_preset_pack(str(EVENTS_PATH), preset_name).events}
        for preset_name in PRESET_CONFIGS
    }
    event_records = []
    for row in sorted(rows, key=lambda item: item["date"]):
        event_records.append(
            {
                "name": row["name"],
                "date": row["date"],
                "family": row.get("family") or "",
                "subtype": row.get("subtype") or "",
                "region": row.get("region") or "",
                "tags": list(row.get("tags") or []),
                "notes": row.get("notes") or "",
                "presets": sorted(
                    [
                        preset_name
                        for preset_name in PRESET_CONFIGS
                        if row["name"] in preset_membership[preset_name]
                    ]
                ),
            }
        )

    family_counts = Counter(row.get("family") or "Other" for row in rows)
    overview = {
        "cards": [
            {"label": "Presets", "value": str(len(presets_payload)), "detail": "Deployable research modes"},
            {"label": "Events", "value": str(len(rows)), "detail": "Historical catalysts in the library"},
            {"label": "Assets", "value": str(frame.shape[1]), "detail": "Series successfully loaded for this snapshot"},
        ],
        "families": [
            {"family": family, "count": count}
            for family, count in family_counts.most_common(6)
        ],
        "recentEvents": list(reversed(event_records[-6:])),
    }

    asset_records = []
    for asset in ASSETS:
        coverage = int(frame[asset["key"]].dropna().shape[0]) if asset["key"] in frame.columns else 0
        asset_records.append(
            {
                "key": asset["key"],
                "label": asset["key"],
                "displayLabel": display_label(asset["key"]),
                "source": asset["source"],
                "symbol": asset["symbol"],
                "category": asset["category"],
                "coverage": coverage,
            }
        )

    metadata = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "defaultPreset": default_preset,
        "presetCount": len(presets_payload),
        "eventCount": len(rows),
        "startDate": frame.index.min().strftime("%Y-%m-%d"),
        "endDate": frame.index.max().strftime("%Y-%m-%d"),
        "fred": asdict(fred_status),
        "assets": asset_records,
    }

    write_json(PUBLIC_DATA_DIR / "metadata.json", metadata)
    write_json(PUBLIC_DATA_DIR / "presets.json", presets_payload)
    write_json(PUBLIC_DATA_DIR / "events.json", event_records)
    write_json(PUBLIC_DATA_DIR / "overview.json", overview)

    print(f"Snapshot export complete: {len(rows)} events, {len(presets_payload)} presets, {frame.shape[1]} assets.")
    print(
        "FRED summary: "
        f"requested={fred_status.requested}, "
        f"loaded={len(fred_status.loaded)}, "
        f"skipped_no_key={len(fred_status.skippedNoKey)}, "
        f"failed_provider={len(fred_status.failedProvider)}"
    )


if __name__ == "__main__":
    main()
