# SQL Layers

- `staging/`: typed, renamed, and code-translated source views
- `marts/`: dimensions, facts, bridge, and business-facing analytical marts
- `analysis/`: readable question-driven SQL used by reports and the dashboard
- `quality/`: reserved for standalone zero-row SQL files; the current executable assertion registry is `src/retail_bank_analytics/quality.py`

Every SQL file added later must declare its grain, key assumptions, and expected output.

`marts/080_growth.sql` builds the complete-month lifecycle spine and day-180 card-adoption landmark after the core and portfolio layers. Dashboard/report consumers use the governed `analytics.*` views. Source fixture tests execute this same file and explicitly test gaps, partial months, feature cutoffs and censored outcomes.
