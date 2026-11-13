"""Trusted historical snapshot and explicitly curated official quarterly indicators."""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = ROOT / "data" / "historical_snapshot.json"
LATEST = ROOT / "data" / "latest_verified.json"


@lru_cache(maxsize=1)
def historical() -> dict:
    return json.loads(HISTORICAL.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def quarterly_release() -> dict:
    return json.loads(LATEST.read_text(encoding="utf-8"))


def market_summary() -> dict:
    """Annual values share a period. Latest quarterly indicators are separate."""
    data = historical()
    total = data["seg_gwp"]["Total"]
    annual = {
        "period": "FY2025",
        "classification": "OFFICIAL (legacy transcription; independent reconciliation pending)",
        "gwp_sar_m": total["2025"],
        "gwp_growth_pct": round(100 * (total["2025"] / total["2024"] - 1), 2),
        "combined_ratio_pct": data["market"]["combined_ratio"]["2025"],
        "net_income_sar_m": data["market"]["net_income"]["2025"],
        "solvency_margin_pct": data["market"]["solvency_avg"]["2025"],
        "source": "IA Saudi Insurance Market Report 2025; see Data & Sources",
    }
    return {"annual": annual, "quarterly": quarterly_release()}


def evidence_context() -> str:
    d = market_summary()
    q = d["quarterly"]
    lines = ["FY2025 annual market indicators (historical prototype data):",
             json.dumps(d["annual"], ensure_ascii=False),
             "Q1 2026 verified published quarterly indicators, NOT directly comparable with full-year FY2025:",
             json.dumps(q, ensure_ascii=False)]
    return "\n".join(lines)
