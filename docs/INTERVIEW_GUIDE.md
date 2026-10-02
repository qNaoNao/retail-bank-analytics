# Interview Guide

## Project name for a résumé

**Retail Bank Customer 360 & Risk Analytics | SQL, DuckDB, Python, Streamlit**

## Résumé bullets

- Built a reproducible DuckDB analytical warehouse integrating eight relational banking tables and 1.06M transactions into governed customer, account, cohort, product, and lending-risk marts.
- Authored SQL with multi-table joins, CTEs, window functions, conditional aggregation, cohort grids, and as-of feature windows; validated the output with 20 automated data assertions.
- Developed a Streamlit/Plotly decision dashboard with portfolio filters, customer/account drill-down, onboarding funnel, cohort analysis, and loan-risk views, supported by 11 automated tests.
- Prevented double counting through an account-client bridge and owner-only money attribution; prevented target leakage by limiting risk features to transactions before loan origination.
- Identified product-engagement and pre-loan risk patterns while explicitly rejecting unsupported churn and causal claims.

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

The finished project rebuilds locally from source, passes 20 data-quality assertions and 11 pytest tests, and supports a live five-page dashboard. Findings include a 10.3% conjunctive 12-month product-adoption stage and strong descriptive differences in pre-loan payment burden, while the cohort audit shows why the data cannot support a credible churn model.

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

### How is target leakage prevented?

Loan features join transactions only when `transaction_date < loan_date`. An automated assertion fails if the feature-window end reaches or passes origination. Loan outcome and post-loan balance are never input features.

### Why not call activity retention “customer retention”?

The source has transactions but no closure, cancellation, dormancy policy, or customer-exit label. Continued transactions are only an activity proxy.

### Why no production model?

Only 234 loans have finished outcomes and only 31 defaulted. A baseline could be educational, but a headline accuracy would be unstable and easy to misuse. The project retains leakage-safe features and a model gate, prioritising analysis that can be defended.

## 10-minute walkthrough structure

1. Business problem and users — 1 minute
2. Data source, grains, and bridge — 2 minutes
3. Pipeline and quality controls — 2 minutes
4. Dashboard findings — 3 minutes
5. Limits, recommendations, and what data comes next — 2 minutes

