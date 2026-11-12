# Saudi Insurance Intelligence Cockpit — Architecture Audit
Date: 2026-11-12
Repository: bendbabis/saudi-insurance-cockpit
Base: main

## As-is
- Single `index.html` (~89 KB), inline CSS, inline JavaScript, Chart.js 4.4.1 from CDN.
- All data is embedded in the browser in the `D` object (historical annual market statistics, segment premiums, line statistics, solvency, structures and source listings).
- Eight tabs: Overview, Lines, Motor & Health, Capital & Reinsurance, Market Structure, Signals, Actuarial Twin, Data & Sources.
- The Actuarial Twin uses hardcoded FY2025 segment baselines, parameter sliders, synthetic insurer allocation, derived profitability and a 2,000-draw Monte Carlo.
- Strong existing domain coverage and excellent material to preserve. Do not remove this analytical baseline without parity tests.

## Material issues
1. **Data freshness**: a static FY2025 dataset is not automatically updated with later releases. The IA has a Q1 2026 report, published September 2026, which must remain separate from full-year FY2025 statistics.
2. **Data lineage**: chart source labels exist, but metric-level provenance, download receipts, revision history and validation are absent.
3. **Security**: no backend exists, so putting an LLM provider key in browser code would expose it publicly.
4. **Modularity**: monolithic code hinders changes, testing and reliable reuse.
5. **Actuarial methodology**: model assumptions are sometimes synthetic; NWP used as a proxy for net earned premium in the legacy simulation. IFRS17 comparisons require care across reporting changes.
6. **Governance**: company-level private supervisory data is not available; a public market view must not imply internal insurer ratings.
7. **Quality**: no automated tests, end-to-end tests or deployment instructions currently present.

## P0 implementation architecture
- Preserve `index.html` and existing views while adding an executive companion layer; keep the original available without API access.
- FastAPI backend with server-side LLM calls and sourced market data API.
- JSON seed exported from the existing `D` dataset with a versioned `historical_snapshot.json`.
- Durable SQLite document/source registry for monitored official reports; authorized scheduled discovery and a manual refresh endpoint.
- Source cards with status, timestamp and direct links; new releases are not silently treated as validated numeric datasets.
- Deterministic scenario calculations backed by unit tests and clear proxy labels.
- Optional Anthropic/OpenAI conversational assistant, grounded in snapshot plus source register; disabled with an explicit configuration warning until a server-side API key is provided.
- GitHub Actions CI, environment configuration, requirements and documentation.

## P1/P2
- Versioned metric warehouse and audited table extraction; quarter/year dimensional modeling.
- Company-level benchmarking from licensed Tadawul and issuer disclosures.
- Document-level RAG, page citations, multilingual Arabic/English and role-aware intelligence.
- More sophisticated IFRS17 projection, financial bridge and empirically calibrated stochastic risk modelling.
- Enterprise authentication, managed Postgres, asynchronous jobs and hosted production deployment.

## Guardrails
- Official reported / modelled / estimated / synthetic must be visibly distinct.
- IA Q1 2026 metrics are not comparable to FY2025 absolute amounts without matching Q1 2025 periods.
- Missing credentials mean an unavailable AI feature, not a pretend functional chatbot.
- No API secrets in repository, frontend assets or logged requests.
- No official regulatory scoring claims without verified rules and source data.
