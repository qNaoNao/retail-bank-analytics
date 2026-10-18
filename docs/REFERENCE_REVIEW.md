# Reference Review and Implemented Improvements

Reviewed 2026-10-19. These references informed design choices; repository claims were not treated as verified benchmarks. The implementation in this project is independent. No source code or historical datasets from these repositories were copied into this repository.

| Reference and material inspected | Useful idea | Applied here | Deliberate adaptation |
|---|---|---|---|
| [dbt-labs/jaffle-shop](https://github.com/dbt-labs/jaffle-shop), especially [`orders.yml`](https://github.com/dbt-labs/jaffle-shop/blob/main/models/marts/orders.yml) and [`orders.sql`](https://github.com/dbt-labs/jaffle-shop/blob/main/models/marts/orders.sql) | Keep grain, metric definitions, relationship checks and small scenario tests together | SQL growth marts, executable reconciliation assertions, hand-calculated boundary/gap tests, and a source-free full-pipeline test | Keep the existing DuckDB pipeline; adding a dbt dependency alone would not improve the underlying analysis |
| [Customer Analytics & Churn Prediction Platform](https://github.com/yuqing-adele/An-end-to-end-customer-analytics-and-churn-prediction-platform), README architecture / demo instructions | A reviewer should be able to run the dashboard without obtaining the full warehouse; fixed source observation dates make results stable | Independent deterministic synthetic warehouse and source-selectable dashboard; source-derived as-of date; offline HTML report | No real customer snapshots are committed. Synthetic figures are labelled and cannot generate the historical findings report. The other project's model scores are not claims about this project |
| [Game Analytics SQL Portfolio](https://github.com/Kou2ka/game-analytics-sql-portfolio), README metric and analysis-module descriptions | Split active-user growth into lifecycle components, respect observable windows, check composition, and distinguish a campaign response from a treatment effect | Dense account-month calendar, new / retained / reactivated / newly inactive bridge, landmark-based issuance windows, opening-year standardization and prospective experiment planning | This bank source has no randomized campaign, channels, acquisition cost or revenue. No treatment effect, CAC, LTV or ROI is invented |

## Statistical references

- [Statsmodels proportion intervals](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html): Wilson score interval for a binary rate. The implementation uses the standard library; its historical 31/234 result was cross-checked against SciPy's Wilson interval.
- [Statsmodels independent-sample power documentation](https://www.statsmodels.org/stable/generated/statsmodels.stats.power.NormalIndPower.html): background on normal-approximation, fixed-horizon planning. This project explicitly uses an equal-allocation two-proportion formula, with the approximation and assumptions exposed next to the result.

## Findings from reviewing the existing project

1. The warehouse already had useful source contracts, owner-only attribution, loan feature cutoffs and reproducible SQL. Preserve these.
2. A 100% activation rate and near-100% activity proxy cannot justify a retention opportunity or a churn model. Show the saturation and choose a measurable endpoint.
3. Code-only CI previously skipped warehouse and application tests when the historical database was missing. A complete independently generated source fixture now exercises all SQL layers and the application in that situation.
4. An empty customer selection previously caused the risk page to show all loans. It now shows zero loans.
5. Dashboard query caching previously ignored database rebuilds and data-source changes. It now includes the resolved database path and file modification version.

## Remaining limits

This is a stronger analytics portfolio, not an operating internet product. It has no event instrumentation, real exposure/assignment logs, production SLA or measured campaign uplift. The next project for a product-growth-specific role should use actual event-level funnels and a genuine randomized experiment dataset. This project demonstrates transferable SQL, measurement and experimental-design reasoning on a banking domain.
