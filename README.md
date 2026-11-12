# Saudi Insurance Intelligence Cockpit

The original eight-tab HTML cockpit is preserved. A new executive companion view adds curated Q1 2026 statistics, a server-calculated scenario engine, official-source discovery, and an optional server-side AI assistant.

## Local execution
Requires Python 3.11+.

1. Create a virtual environment and install requirements: `pip install -r requirements.txt`
2. Optionally copy `.env.example` to `.env` and load variables in your runtime.
3. Start backend: `uvicorn app.main:app --reload`
4. Open http://localhost:8000/ and select **Executive Command Center**.
5. API docs: http://localhost:8000/docs
6. Tests: `pytest -q`

## AI setup
Set `AI_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` on the server, or `AI_PROVIDER=openai` and `OPENAI_API_KEY`. Optionally set `AI_MODEL`. Do not put secrets in frontend code or GitHub. Without a provider key AI is safely disabled. No paid provider calls occur until one is configured.

## Source discovery
Run `python -m app.refresh` manually or through an approved cron / orchestration scheduler. Discovery stores URLs (not vetted numbers) in SQLite. To trigger the API refresh, set `SIIC_ADMIN_TOKEN` and supply the value as header `X-Admin-Token` on POST /api/market/sources/refresh. Do not expose that administrative endpoint without proper network controls.

## Deployment
`docker build -t siic .` then `docker run -p 8000:8000 --env-file .env siic`. Mount persistent storage for the source registry and set SIIC_DB_PATH. Static GitHub Pages mode displays the classic cockpit, but the executive experience requires a Python backend. Docker mode is not yet production hardened: add user authentication, HTTPS, reverse-proxy ingress and observability before public deployment.

## Limitations
Data classifications and assumptions are in docs/METHODOLOGY.md. Source discovery does not constitute a validated data refresh; LLM is snapshot-grounded, not RAG. This is a P0 prototype, not a regulatory-grade production platform.
