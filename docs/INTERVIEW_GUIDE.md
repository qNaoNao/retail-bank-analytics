# Interview Guide

## Project name for a résumé

**Retail Bank Customer 360 & Risk Analytics | SQL, DuckDB, Python, Streamlit**

## Résumé bullets

- Built a reproducible DuckDB analytical warehouse integrating eight relational banking tables and 1.06M transactions into governed customer, account, cohort, product, and lending-risk marts.
- Authored SQL with multi-table joins, CTEs, window functions, conditional aggregation, cohort grids, dense activity spines and as-of feature windows; validated the output with 28 automated data assertions.
- Developed a six-tab Streamlit/Plotly dashboard with portfolio filters, account drill-down, growth decomposition, cohort analysis, card-offer experiment planning and loan-risk views; supported by 34 tests on the historical-data setup.
- Prevented double counting through an account-client bridge and owner-only money attribution; prevented target leakage by limiting risk features to transactions before loan origination.
- Identified product-engagement and pre-loan risk patterns while explicitly rejecting unsupported churn and causal claims.
- Defined a day-180 landmark and disjoint 180-day outcome for card issuance (179/4,500, 3.98%); reported Wilson intervals, checked opening-year composition, and quantified experimental sample size and maturation time without claiming observed uplift.
- Created independently generated eight-table fixtures so a source-only clone runs full SQL/application checks without redistributing the historical data.

## STAR story

### Situation

A retail bank has customer, account, transaction, product, loan, and demographic information spread across eight legacy tables. Business teams cannot safely compare customers or define one version of portfolio metrics.

### Task

Create a reproducible analytical product for growth, customer, BI, and risk users. It must demonstrate strong SQL and modelling, expose metric definitions, and avoid unsupported claims.

### Action

1. Audited source shape, keys, missingness, and file checksums before transformation.
2. Built raw, staging, dimensional, and analytical layers in DuckDB.
3. Modelled customer-account permissions as a bridge and attributed money metrics only to account owners.
4. Created account-month, customer 360, cohort, onboarding, and origination-time loan-risk marts.
5. Added zero-row SQL assertions, reconciliation tests, leakage checks, and a Streamlit render test.
6. Designed the dashboard around decisions and placed interpretation limits next to the charts.

### Result

The project rebuilds locally from source, passes 28 data-quality assertions and 34 pytest tests, and supports a six-tab dashboard plus an offline decision report. Findings include a 10.3% conjunctive 12-month card-or-loan funnel stage and a distinct 3.98% subsequent 180-day card-issuance baseline. The prospective planner shows that a 1 percentage-point effect would require about 13,428 accounts, beyond the historical 4,500-account pool. No real treatment effect or realized revenue improvement was measured.

### Reflection

The strongest lesson was that trustworthy analytics sometimes rejects a requested story. A 99.8% activity proxy is not evidence of extraordinary retention; it is evidence that the source lacks a discriminating churn outcome.

## Technical questions and answer anchors

### Why DuckDB?

The target is analytical SQL on a laptop, not transactional application traffic. DuckDB supports window functions, Parquet, fast columnar scans, and zero-server reproducibility on macOS. PostgreSQL would add administration without improving the portfolio’s main evidence.

### How did you prevent customer/account double counting?

`disposition` is a permission bridge: 4,500 owners plus 869 authorized users. Money remains at account grain. Customer 360 joins only the `owner` relationship; authorized-user analysis is separate.

### Where are window functions used?

- `ROW_NUMBER` chooses the deterministic month-ending balance.
- `NTILE` creates transparent balance and activity quartiles.
- `LAG` and `FIRST_VALUE` calculate funnel stage conversion.
- A generated relative-month grid supports cohort analysis without survivor-only joins.
- A dense month spine plus `LAG` and prior-row cumulative sums separates new, retained, reactivated and newly inactive accounts. It reconciles to the observed monthly active-account change.

### How is target leakage prevented?

Loan features join transactions only when `transaction_date < loan_date`. An automated assertion fails if the feature-window end reaches or passes origination. Loan outcome and post-loan balance are never input features.

### Why not call activity retention “customer retention”?

The source has transactions but no closure, cancellation, dormancy policy, or customer-exit label. Continued transactions are only an activity proxy.

### Why no production model?

Only 234 loans have finished outcomes and only 31 defaulted. A baseline could be educational, but a headline accuracy would be unstable and easy to misuse. The project retains leakage-safe features and a model gate, prioritising analysis that can be defended.

### What makes the growth analysis relevant to an internet company?

The domain is banking, but the work demonstrates lifecycle accounting, denominator control, incomplete follow-up handling, pre-outcome feature windows, composition effects, uncertainty and experimental feasibility. It does not demonstrate web instrumentation, advertising attribution or a completed online experiment; those need additional event/exposure data.

### Why is 100% activation a useful negative finding?

Every account meets the current 30-day operation definition, so improving that endpoint cannot be demonstrated in this sample. Rather than promising an activation increase, the project chooses a narrower card-issuance outcome with a non-saturated baseline and shows its limitations.

### Does the transfer segment's card rate prove whom we should target?

No. The raw rates are 5.11% without a recorded early outgoing transfer and 3.53% with one. Applying common opening-year weights barely changes them, but this only addresses year composition. It does not measure incrementality, consent, suitability or unobserved customer differences. Randomized assignment is still required.

### What does the sample-size result actually say?

With a historical baseline of 3.98%, a two-sided 5% test and 80% power, a 1 pp MDE needs about 6,714 accounts per arm. A 2 pp MDE needs about 1,856 per arm. At an **assumed** 50 newly eligible accounts/day, the latter takes at least 75 recruitment days plus 180 outcome days. Historical cohorts are not simultaneous recruitment traffic, and neither MDE is an observed treatment effect.

### What does CI prove without raw data?

The synthetic fixture executes every transformation layer, portable assertions and dashboard interactions. Hand-calculated histories separately verify gaps, month completeness, landmark boundaries, immature labels and composition reversal. Historical source-count tests are skipped with an explicit reason when the historical warehouse is absent; synthetic values do not substitute for historical findings.

## 10-minute walkthrough structure

1. Business problem and users — 1 minute
2. Data source, grains, and bridge — 2 minutes
3. Pipeline and quality controls — 2 minutes
4. Dashboard findings — 3 minutes
5. Limits, recommendations, and what data comes next — 2 minutes

