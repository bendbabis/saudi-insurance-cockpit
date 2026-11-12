# Market intelligence and scenario methodology

## Observed vs modelled
- **FY2025**: historical annual values transcribed in the existing cockpit, pending independent metric-level reconciliation. Original Data & Sources tab has report/page references.
- **Q1 2026**: curated metrics from [Insurance Authority, 8 September 2026](https://www.ia.gov.sa/en/media-center/news/128): SAR 29.8bn GWP, +14.4% YoY, 98.3% net combined ratio, SAR 18.5bn health GWP, SAR 5bn motor GWP, 11.2m insured vehicles and domestic reinsurance capacity of 37% of ceded premium.
- Q1 2026 amounts must never be compared directly with FY2025 absolute values as if periods matched.

## Deterministic scenario proxy
Baseline GWP (SAR m): Motor 15,590, Health 47,750, P&C 12,780, Protection & Savings 8,160. Sector income baseline SAR 1,900m, investment income SAR 2,240m. Retention, P&C and P&S combined ratios and capital are assumed legacy prototype inputs.

Gross premium = base GWP × rate factor × exposure factor.
Earned premium proxy = GWP × retention.
Claims = baseline proxy premium × baseline claims ratio × exposure growth × unit cost inflation, plus selected ratio shocks.
Expenses = scenario proxy premium × shifted expense ratio.
Underwriting result = proxy premium − claims − expenses − catastrophe shock.
Projected income = baseline income + underwriting change + investment income change.
Available capital proxy = assumed base capital + projected income − payout of positive income + injections.
Required capital proxy = assumed baseline requirement × scenario GWP / baseline GWP × capital uplift.

This is NOT an IFRS 17 insurance revenue model, validated regulatory capital model, actuarial forecast, or official supervisory score. Baseline 25,000m available capital and the synthetic insurer distribution in the original Twin are not actual insurer positions.

## Source monitor
Discovery reads allowlisted official index pages, stores detected links and timestamps in SQLite, and flags all discovered links UNVERIFIED. It does not extract, reconcile or publish new numerical values. Scheduling is an operator responsibility.

## AI
A backend-only provider API key enables the assistant to explain the structured FY2025 and Q1 2026 data. No page-level RAG, insurer benchmarking, automatic AI tool calls or web research exists yet. The assistant must acknowledge missing evidence.
