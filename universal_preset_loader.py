from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

import yaml


PRESET_CONFIGS: dict[str, dict[str, Any]] = {
    "Middle East Conflict": {
        "trigger_asset": "Brent Futures",
        "sim_pool_base": [
            "VIX",
            "Gold",
            "DXY",
            "S&P 500",
            "US 10Y Yield",
            "US HY OAS",
            "EURUSD",
            "USDJPY",
            "Copper",
            "Shipping (BDRY)",
        ],
        "weights": {"quant": 0.50, "tag": 0.30, "macro": 0.20},
    },
    "US CPI": {
        "trigger_asset": "US 2Y Yield",
        "sim_pool_base": [
            "S&P 500",
            "DXY",
            "US 10Y Yield",
            "VIX",
            "Gold",
            "US HY OAS",
        ],
        "weights": {"quant": 0.55, "tag": 0.25, "macro": 0.20},
    },
    "US NFP": {
        "trigger_asset": "US 2Y Yield",
        "sim_pool_base": [
            "S&P 500",
            "DXY",
            "US 10Y Yield",
            "VIX",
            "Gold",
            "US HY OAS",
        ],
        "weights": {"quant": 0.55, "tag": 0.25, "macro": 0.20},
    },
    "US PCE": {
        "trigger_asset": "US 2Y Yield",
        "sim_pool_base": [
            "S&P 500",
            "DXY",
            "US 10Y Yield",
            "VIX",
            "Gold",
            "US HY OAS",
        ],
        "weights": {"quant": 0.55, "tag": 0.25, "macro": 0.20},
    },
    "US Elections": {
        "trigger_asset": "S&P 500",
        "sim_pool_base": [
            "DXY",
            "US 10Y Yield",
            "VIX",
            "Gold",
            "EURUSD",
            "USDJPY",
            "US HY OAS",
        ],
        "weights": {"quant": 0.55, "tag": 0.25, "macro": 0.20},
    },
    "Custom": {
        "trigger_asset": "Brent Futures",
        "sim_pool_base": [
            "VIX",
            "Gold",
            "DXY",
            "S&P 500",
            "US 10Y Yield",
        ],
        "weights": {"quant": 0.50, "tag": 0.30, "macro": 0.20},
    },
}


@dataclass(frozen=True)
class PresetPack:
    events: list[tuple[str, str]]
    all_tags: list[str]
    event_tags: dict[str, set[str]]
    macro_context: dict[str, dict[str, Any]]


def _parse_note_number(notes: str, key: str) -> float | None:
    if not notes:
        return None
    m = re.search(rf"{re.escape(key)}\s*=\s*([-+]?\d+(?:\.\d+)?)", notes)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _default_macro(family: str) -> dict[str, Any]:
    fam = (family or "").lower()
    if "geopolitics" in fam or "energy" in fam:
        return {"trigger": 70, "cpi": "mid", "fed": "hold"}
    if "inflation" in fam or "labor" in fam:
        return {"trigger": 4, "cpi": "mid", "fed": "hold"}
    if "fomc" in fam:
        return {"trigger": 4, "cpi": "mid", "fed": "hiking"}
    if "election" in fam:
        return {"trigger": 4200, "cpi": "mid", "fed": "hold"}
    return {"trigger": 50, "cpi": "mid", "fed": "hold"}


def _include_row(row: dict[str, Any], preset: str) -> bool:
    family = (row.get("family") or "").strip()
    tags = set(row.get("tags") or [])
    if preset == "Middle East Conflict":
        return family in {"Geopolitics", "Commodities/Energy"} or bool(tags.intersection({"military_conflict", "energy_shock", "shipping_disruption", "sanctions"}))
    if preset == "US CPI":
        return family == "US Inflation" and ("cpi" in tags or "CPI" in (row.get("name") or ""))
    if preset == "US NFP":
        return family == "US Labor" and ("nfp" in tags or "NFP" in (row.get("name") or ""))
    if preset == "US PCE":
        return family == "US Inflation (PCE)"
    if preset == "US Elections":
        return family == "Elections"
    if preset == "Custom":
        return True
    return False


def load_preset_pack(library_path: str, preset: str) -> PresetPack:
    raw = yaml.safe_load(open(library_path, "r", encoding="utf-8")) or {}
    rows: list[dict[str, Any]] = raw.get("events") or []

    events: list[tuple[str, str]] = []
    event_tags: dict[str, set[str]] = {}
    macro_context: dict[str, dict[str, Any]] = {}
    all_tags: set[str] = set()

    for row in rows:
        if not _include_row(row, preset):
            continue
        name = str(row.get("name") or "").strip()
        dt = str(row.get("date") or "").strip()
        if not name or not dt:
            continue
        tags = {str(t).strip() for t in (row.get("tags") or []) if str(t).strip()}
        notes = str(row.get("notes") or "")
        family = str(row.get("family") or "")

        events.append((name, dt))
        event_tags[name] = tags
        all_tags.update(tags)

        d = _default_macro(family)
        actual_val = _parse_note_number(notes, "actual")
        if actual_val is not None:
            d["trigger"] = actual_val
        if "cut" in (row.get("subtype") or "").lower():
            d["fed"] = "cutting"
        elif "hike" in (row.get("subtype") or "").lower():
            d["fed"] = "hiking"
        macro_context[name] = d

    # Keep deterministic order by date
    events = sorted(events, key=lambda x: x[1])
    return PresetPack(
        events=events,
        all_tags=sorted(all_tags) if all_tags else ["event"],
        event_tags=event_tags,
        macro_context=macro_context,
    )
