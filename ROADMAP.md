# 9-Day Delivery Roadmap

Each day ends with a visible, testable artifact. If time is compressed to seven days, Days 6–7 and Days 8–9 can be paired; the core analytical quality bar should not be reduced.

| Day | Milestone | Main artifact | Learning and interview focus |
|---|---|---|---|
| 1 | Scope and foundation | Spec, dataset decision, environment, repository skeleton, smoke tests | Explain why the data and business scope were chosen |
| 2 | Acquisition and audit | Reproducible download, raw inventory, schema profile, data-quality report | Separate source defects from transformation defects |
| 3 | Warehouse staging | DuckDB raw/staging tables, translated codes, validated keys and dates | Explain table grain, joins, and why DuckDB fits |
| 4 | Dimensional model and metrics | Dimensions, facts, marts, SQL assertions, metric dictionary v1 | Defend grain, bridge-table handling, and no-double-counting rules |
| 5 | Customer 360 and segments | Explainable value/behaviour segments and SQL analysis | Turn metrics into operationally meaningful groups |
| 6 | Cohort and engagement | Account-opening cohort and active-month retention analysis | Explain the proxy honestly; use window functions correctly |
| 7 | Loan risk and model gate | Risk views plus leakage review; optional baseline only if valid | Distinguish descriptive risk, prediction, and causality |
| 8 | Dashboard product | Streamlit pages, filters, drill-down, chart annotations | Explain information hierarchy and decision workflow |
| 9 | Portfolio packaging | README results, screenshots, demo script, CV bullets, clean Git history | Deliver a concise 3-minute and detailed 10-minute story |

## Optional Day 10

- Deploy to Streamlit Community Cloud or document a stable local demo.
- Rehearse common SQL, metric-definition, data-quality, and modelling questions.
- Audit the public repository from a fresh clone.

## Milestone commit convention

Use small, reviewable commits such as:

```text
chore: initialize reproducible project foundation
feat: ingest and validate Berka source tables
feat: build DuckDB dimensional model and metric marts
feat: add customer and cohort analysis
feat: add lending risk analysis
feat: deliver Streamlit decision dashboard
docs: package recruiter-facing portfolio story
```

Do not rewrite or squash useful learning milestones solely to make the history look artificially perfect.
