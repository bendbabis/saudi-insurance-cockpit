"""Deterministic market proxy model. Not an official regulatory capital calculation."""
from typing import Literal
from pydantic import BaseModel, Field

class ScenarioInputs(BaseModel):
    motor_rate_pct: float = Field(0, ge=-40, le=60)
    motor_cost_pct: float = Field(0, ge=-40, le=80)
    motor_volume_pct: float = Field(0, ge=-40, le=60)
    health_rate_pct: float = Field(0, ge=-40, le=60)
    health_cost_pct: float = Field(0, ge=-40, le=80)
    health_volume_pct: float = Field(0, ge=-40, le=60)
    pc_growth_pct: float = Field(0, ge=-40, le=80)
    pc_claims_pts: float = Field(0, ge=-35, le=40)
    ps_growth_pct: float = Field(0, ge=-40, le=80)
    expense_shift_pts: float = Field(0, ge=-15, le=25)
    investment_change_pct: float = Field(0, ge=-100, le=100)
    catastrophe_sar_m: float = Field(0, ge=0, le=10000)
    rbc_uplift_pct: float = Field(0, ge=0, le=80)
    capital_injection_sar_m: float = Field(0, ge=0, le=20000)
    payout_pct: float = Field(40, ge=0, le=100)


BASE = {
    "Motor": {"gwp":15590.0,"ret":0.991,"cl":84.0,"ex":22.3},
    "Health":{"gwp":47750.0,"ret":0.985,"cl":83.0,"ex":12.7},
    "Property & Casualty":{"gwp":12780.0,"ret":0.27,"cl":58.0,"ex":37.0},
    "Protection & Savings":{"gwp":8160.0,"ret":0.64,"cl":80.0,"ex":16.0},
}
BASE_NET_INCOME=1900.0
BASE_INVESTMENT_INCOME=2240.0
BASE_AVAILABLE_CAPITAL=25000.0
BASE_SOLVENCY=1.56


def simulate(v: ScenarioInputs) -> dict:
    raw = v.model_dump()
    estimates = []
    gross0 = sum(x["gwp"] for x in BASE.values())
    gross1 = 0.0
    earned0 = earned1 = uw0 = uw1 = 0.0
    for name, b in BASE.items():
        if name == "Motor":
            rate, volume, cost, cl_shift = v.motor_rate_pct, v.motor_volume_pct, v.motor_cost_pct, 0
        elif name == "Health":
            rate, volume, cost, cl_shift = v.health_rate_pct, v.health_volume_pct, v.health_cost_pct, 0
        elif name == "Property & Casualty":
            rate, volume, cost, cl_shift = 0, v.pc_growth_pct, 0, v.pc_claims_pts
        else:
            rate, volume, cost, cl_shift = 0, v.ps_growth_pct, 0, 0

        gwp1 = b["gwp"] * (1 + rate / 100) * (1 + volume / 100)
        premium0 = b["gwp"] * b["ret"]
        premium1 = gwp1 * b["ret"]  # deliberately labelled proxy, not IFRS17 insurance revenue
        claims0 = premium0 * b["cl"] / 100
        claims1 = claims0 * (1 + volume / 100) * (1 + cost / 100)
        if cl_shift:
            claims1 += premium1 * cl_shift / 100
        expenses0 = premium0 * b["ex"] / 100
        expenses1 = premium1 * max(0, b["ex"] + v.expense_shift_pts) / 100
        u0, u1 = premium0 - claims0 - expenses0, premium1 - claims1 - expenses1
        cr0 = 100 * (claims0 + expenses0) / premium0
        cr1 = 100 * (claims1 + expenses1) / premium1
        estimates.append({
            "segment": name,
            "baseline_gwp_sar_m": round(b["gwp"], 2),
            "scenario_gwp_sar_m": round(gwp1, 2),
            "baseline_combined_ratio_pct": round(cr0, 2),
            "scenario_combined_ratio_pct": round(cr1, 2),
            "underwriting_delta_sar_m": round(u1-u0, 2),
        })
        gross1 += gwp1
        earned0 += premium0
        earned1 += premium1
        uw0 += u0
        uw1 += u1

    uw1 -= v.catastrophe_sar_m
    underwriting_delta = uw1 - uw0
    investment_delta = BASE_INVESTMENT_INCOME * v.investment_change_pct / 100
    income1 = BASE_NET_INCOME + underwriting_delta + investment_delta
    available1 = (BASE_AVAILABLE_CAPITAL + income1 -
                  max(income1,0) * v.payout_pct / 100 + v.capital_injection_sar_m)
    required0 = BASE_AVAILABLE_CAPITAL / BASE_SOLVENCY
    # Explicit simplified proxy: gross premium scale and an optional regulatory stress uplift.
    required1 = required0 * (gross1 / gross0) * (1 + v.rbc_uplift_pct / 100)
    ratio = 100 * available1 / required1 if required1 else None
    market_cr0 = 100 * (earned0 - uw0) / earned0
    market_cr1 = 100 * (earned1 - uw1) / earned1

    return {
        "classification": "MODELLED",
        "reporting_context": "FY2025 reference / hypothetical forward scenario",
        "inputs": raw,
        "segments": estimates,
        "market": {
            "baseline_gwp_sar_m": round(gross0,2),
            "scenario_gwp_sar_m": round(gross1,2),
            "baseline_combined_ratio_pct": round(market_cr0,2),
            "scenario_combined_ratio_pct": round(market_cr1,2),
            "underwriting_delta_sar_m": round(underwriting_delta,2),
            "investment_delta_sar_m": round(investment_delta,2),
            "scenario_net_income_sar_m": round(income1,2),
            "scenario_solvency_proxy_pct": round(ratio,2) if ratio is not None else None,
            "required_capital_proxy_sar_m": round(required1,2)
        },
        "warnings": [
            "SIMULATED: this is not a regulatory forecast or an official Saudi RBC calculation.",
            "GWP multiplied by assumed retention is used as a proxy for net earned premium; NOT IFRS 17 insurance revenue.",
            "P&C and Protection & Savings loss/expense/retention baselines are assumptions; capital availability is assumed.",
            "Sector segment amounts and proxy measures require independent source reconciliation before external decision use.",
            "The forward solvency proxy is NOT comparable with the official published solvency margin without reconciliation."
        ],
        "source": "Existing cockpit Actuarial Twin FY2025 baseline; see docs/METHODOLOGY.md"
    }


def breakeven_motor_rate(target_combined_ratio_pct: float = 100.0) -> float | None:
    """Assumes cost per exposure fixed and operating expense ratio unchanged."""
    expense = BASE["Motor"]["ex"]
    loss = BASE["Motor"]["cl"]
    if target_combined_ratio_pct <= expense:
        return None
    return round(100 * (loss / (target_combined_ratio_pct - expense) - 1), 2)
