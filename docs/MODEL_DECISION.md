# Model Go/No-Go Decision

## Decision: no promoted model in v1

The dataset contains 682 loans, but only 234 have finished outcomes and only 31 of those defaulted. This is enough to demonstrate leakage-safe feature engineering and exploratory associations, but too small for a stable portfolio headline or credible production policy.

## What is ready

- One row per loan in `mart.loan_risk_features`
- Demographics and district context available at origination
- Account tenure and transaction features restricted to dates before the loan
- Payment burden, balance stress, cash flow, and volatility measures
- Automated assertion that fails if the feature window reaches origination

## Why stopping is the analytical choice

- Repeated cross-validation would reuse the same 31 defaults many times and understate uncertainty.
- A final-year temporal holdout contains only three defaults, so one case materially changes recall.
- Modern underwriting policy, application variables, and macroeconomic context are absent.
- A model could distract from the project’s stronger evidence: SQL, governed metrics, multi-table modelling, and decision-oriented BI.

## What would unlock a model

- A larger set of matured loans across multiple time periods
- Application-time income, affordability, and policy variables
- A defined observation/performance window
- Modern economic context and population-stability checks
- Agreed error costs, threshold policy, fairness review, and calibration monitoring

