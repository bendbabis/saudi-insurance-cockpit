"""Saudi Insurance Intelligence P0 backend."""
import os
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .market import market_summary
from .scenarios import ScenarioInputs, simulate, breakeven_motor_rate
from .sources import catalog, refresh_sources
from .ai import ChatRequest, answer, status

ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title="Saudi Insurance Intelligence Cockpit API",version="0.1.0",
            description="Market data, source registry, deterministic scenarios and optional server-side AI.")

@app.get("/api/health")
def health():
    return {"status":"ok","version":"0.1.0"}

@app.get("/api/market/summary")
def market():
    return market_summary()

@app.get("/api/market/sources")
def sources():
    return catalog()

@app.post("/api/market/sources/refresh")
def refresh(x_admin_token: str | None = Header(default=None)):
    secret=os.getenv("SIIC_ADMIN_TOKEN")
    if not secret or not x_admin_token or x_admin_token != secret:
        raise HTTPException(status_code=403,detail="Admin token is required for manual refresh")
    return refresh_sources()

@app.post("/api/scenarios/run")
def scenario(v: ScenarioInputs):
    return simulate(v)

@app.get("/api/scenarios/motor-breakeven")
def motor_breakeven(target_cr: float=100.0):
    if not 30 <= target_cr <= 150:
        raise HTTPException(status_code=422,detail="Target combined ratio out of range")
    value=breakeven_motor_rate(target_cr)
    return {"target_combined_ratio_pct":target_cr,"required_motor_premium_change_pct":value,
            "classification":"MODELLED","caveat":"Constant claims per exposure and fixed expense ratio; not an observed market forecast."}

@app.get("/api/ai/status")
def ai_status():
    return status()

@app.post("/api/ai/chat")
async def ai_chat(req: ChatRequest):
    return await answer(req)

app.mount("/assets",StaticFiles(directory=str(ROOT/"assets")),name="assets")

@app.get("/",include_in_schema=False)
def index():
    return FileResponse(ROOT/"index.html")
