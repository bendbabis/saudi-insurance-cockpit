from fastapi.testclient import TestClient
from app.main import app
from app.market import market_summary
from app.scenarios import ScenarioInputs, simulate, breakeven_motor_rate
from app.sources import approved_url, discover_links

client=TestClient(app)

def test_health():
    assert client.get("/api/health").json()["status"]=="ok"

def test_period_separation():
    x=market_summary()
    assert x["annual"]["period"]=="FY2025"
    assert x["quarterly"]["reporting_period"]=="2026-Q1"

def test_baseline_no_delta():
    x=simulate(ScenarioInputs())["market"]
    assert x["underwriting_delta_sar_m"]==0
    assert x["scenario_net_income_sar_m"]==1900

def test_cost_shock():
    x=simulate(ScenarioInputs(motor_cost_pct=10,health_cost_pct=10))["market"]
    assert x["scenario_net_income_sar_m"]<1900
    assert x["scenario_combined_ratio_pct"]>x["baseline_combined_ratio_pct"]

def test_motor_pricing():
    base=simulate(ScenarioInputs())["segments"][0]
    new=simulate(ScenarioInputs(motor_rate_pct=10))["segments"][0]
    assert new["scenario_combined_ratio_pct"]<base["scenario_combined_ratio_pct"]

def test_rbc_proxy():
    base=simulate(ScenarioInputs())["market"]
    new=simulate(ScenarioInputs(rbc_uplift_pct=20))["market"]
    assert new["scenario_solvency_proxy_pct"]<base["scenario_solvency_proxy_pct"]

def test_validation():
    assert client.post("/api/scenarios/run",json={"motor_cost_pct":1000}).status_code==422

def test_breakeven():
    assert breakeven_motor_rate(95)>breakeven_motor_rate(100)>0

def test_admin_only_refresh(monkeypatch):
    monkeypatch.delenv("SIIC_ADMIN_TOKEN",raising=False)
    assert client.post("/api/market/sources/refresh").status_code==403

def test_ai_unconfigured(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY",raising=False)
    monkeypatch.setenv("AI_PROVIDER","anthropic")
    assert client.get("/api/ai/status").json()["enabled"] is False
    assert client.post("/api/ai/chat",json={"message":"Market?"}).status_code==503

def test_allowed_links():
    assert approved_url("https://www.ia.gov.sa/en/media-center/news/128")
    assert not approved_url("https://evil.example/report")
    found=list(discover_links('<a href="/en/information-center/reports/quarterly-publications">Quarterly reports</a>',"https://www.ia.gov.sa"))
    assert len(found)==1
