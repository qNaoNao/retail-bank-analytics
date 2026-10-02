# Dashboard QA Record

Date: 2026-10-03 (Australia/Sydney)

## Automated checks

- Streamlit application render smoke test: passed
- Full pytest suite: 11 passed
- Ruff application and package lint: passed
- Warehouse assertions feeding the dashboard: 20 passed

## Visual checks

The local application was opened at `http://127.0.0.1:8501` and checked in the Codex in-app browser.

| View | Result | Checks performed |
|---|---|---|
| Executive overview | Pass | KPI cards, monthly activity, inflow/outflow, decision note |
| Customer 360 | Pass | filters, segment chart, scatter plot, account selector, balance drill-down |
| Cohort & funnel | Pass | cohort heatmap, conjunctive funnel, activity-retention warning |
| Lending risk | Pass | outcome cards, status mix, payment burden, regional sample-size view |
| Definitions | Pass | metric rules, owner-only attribution, source limitations |

Browser console errors: none observed.

## Responsive observation

The dashboard remains usable in the narrow in-app browser: KPI cards stack vertically, the tab row scrolls, and charts resize to the available width. The default sidebar starts collapsed to protect chart space; users can expand it to change filters.
