# Analysis Findings

All amounts are historical Czech koruna (CZK). Findings are descriptive associations, not causal effects.

## Executive portfolio

- The analytical layer covers **4,500 customers**, **4,500 accounts**, and **1,056,320 transactions**.
- Recorded inflow is **CZK 3,227.5 million** and outflow is **CZK 3,030.3 million**.
- Average monthly ending balance is **CZK 34,774**; **288 accounts (6.4%)** went below zero at least once.
- Average monthly active accounts rose from **614 in 1993** to **4,474 in 1998**. This mainly reflects portfolio build-out, not proven same-customer engagement growth.

## Customer value and product engagement

| Behaviour segment | Customers | Avg. month-end balance | Card penetration | Loan penetration | Loan customers |
|---|---:|---:|---:|---:|---:|
| `core` | 2,526 | 31,758 | 16.7% | 13.9% | 350 |
| `high_activity_mass` | 733 | 30,157 | 9.7% | 16.9% | 124 |
| `high_value_low_engagement` | 427 | 53,063 | 51.1% | 19.4% | 83 |
| `low_activity_low_balance` | 422 | 17,058 | 0.0% | 2.6% | 11 |
| `high_value_engaged` | 392 | 54,464 | 46.2% | 29.1% | 114 |

- **3,096 accounts (68.8%)** have neither a card nor loan; 722 are card-only, 512 are loan-only, and 170 hold both.
- Among accounts with a full 12-month observation window, **464 of 4,500 (10.3%)** reached the conjunctive funnel stage of early activation, sustained six-month engagement, and card-or-loan adoption within 12 months.
- This identifies a product-adoption gap for investigation. It does not prove eligibility, propensity, or treatment uplift; those require policy filters and an experiment.

## Cohort and retention limitation

- Weighted 12-month customer-operation activity retention is **99.8%**. The near-saturated rate provides little churn discrimination.
- The defensible conclusion is that the dataset supports opening-cohort engagement and balance trajectories, but **not true churn modelling**, because account closure and customer-exit labels are absent.

## Lending risk

- Of 234 finished loans, 31 defaulted: a mature-loan problem rate of **13.25%**.
- Defaulted loans averaged **CZK 140,721**, versus **CZK 91,641** for repaid loans.
- Average scheduled-payment-to-pre-loan-monthly-inflow was **33.5%** for defaulted loans and **17.9%** for repaid loans.
- **25.8%** of defaulted borrowers had a negative balance before origination versus **0.0%** of repaid borrowers in this sample.
- These pre-origination associations support further underwriting/back-testing analysis. They are not a modern credit policy, and the sample contains only 31 defaults.

## Recommended actions

1. Review high-value segments for product eligibility, then validate offers with a controlled campaign rather than treating descriptive penetration gaps as uplift.
2. Separate account activation from product adoption in management reporting; activity is nearly universal, while 12-month product adoption is selective.
3. Back-test payment burden and pre-loan negative-balance flags as transparent risk indicators on newer, policy-representative data.
4. Do not build a churn model from this source. Acquire closure/contact data before making retention claims.

## Interpretation boundaries

- Historical 1990s behaviour is not current market sizing.
- Full-lifetime customer segments must not be used as origination-time risk predictors.
- Regional and segment risk rates can be unstable where loan counts are small.
- A recommendation is a proposed next action; it is not an observed business impact.
