# Dashboard QA Record

## Version 0.2 — 2026-10-19 (Asia/Shanghai)

| Verification | Result |
|---|---|
| Historical source-to-warehouse rebuild | Pass; 28 executable assertions |
| Full local Python 3.11 test suite | 34 passed |
| Source-only snapshot, no historical files or database | 28 passed; six historical-only tests explicitly skipped |
| Ruff and whitespace/diff validation | Pass |
| Independent synthetic demo | 240 accounts, eight raw tables, all SQL layers, 25 portable assertions |
| Historical versus synthetic application mode | Explicit source selection, banner and separate databases verified |
| Growth month bridge | December 1998: 4,478 + 0 + 2 − 56 = 4,424 |
| Experiment control | Changing MDE from 2 pp to 1 pp recalculates total 3,712 → 13,428 and displays insufficient-pool warning |
| Offline HTML report | Charts, memo and tables render in a local browser; Plotly library embedded |
| Remote CI / public deployment | Not run this round; changes were not pushed |

New tests include an absent activity month, return after a gap, incomplete final month, exact day-180/day-360 boundaries, immature outcome NULLs, Wilson endpoint rates, infeasible experiment size, opening-year composition reversal, failed-build preservation, empty sidebar filters and rejection of synthetic input to a historical report.

Visual review used a local browser. The growth chart titles/labels remain readable in a narrow viewport; KPI cards stack and the tab strip scrolls. The independent preview uses port 8599 to avoid the user's other projects. Screenshots are in `docs/images/`.

## Original version — 2026-10-03 (Australia/Sydney)

## Automated checks

- Streamlit application render smoke test: passed
- Full pytest suite: 11 passed
- Ruff application and package lint: passed
- Warehouse assertions feeding the dashboard: 20 passed

## Visual checks

The local application was opened at `http://127.0.0.1:8501` and checked in a local browser.

| View | Result | Checks performed |
|---|---|---|
| Executive overview | Pass | KPI cards, monthly activity, inflow/outflow, decision note |
| Customer 360 | Pass | filters, segment chart, scatter plot, account selector, balance drill-down |
| Cohort & funnel | Pass | cohort heatmap, conjunctive funnel, activity-retention warning |
| Lending risk | Pass | outcome cards, status mix, payment burden, regional sample-size view |
| Definitions | Pass | metric rules, owner-only attribution, source limitations |

Browser console errors: none observed.

## Responsive observation

The dashboard remains usable in a narrow browser viewport: KPI cards stack vertically, the tab row scrolls, and charts resize to the available width. The default sidebar starts collapsed to protect chart space; users can expand it to change filters.
