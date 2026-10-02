# Data Quality Report

Generated: 2026-10-02T21:41:06.644737+00:00

Overall status: **PASS**

| Assertion | Failed rows | Status |
|---|---:|---|
| `raw_account_row_count` | 0 | pass |
| `raw_transaction_row_count` | 0 | pass |
| `duplicate_transaction_key` | 0 | pass |
| `orphan_disposition_account` | 0 | pass |
| `orphan_disposition_client` | 0 | pass |
| `orphan_transaction_account` | 0 | pass |
| `orphan_loan_account` | 0 | pass |
| `orphan_card_disposition` | 0 | pass |
| `invalid_loan_status` | 0 | pass |
| `invalid_transaction_direction` | 0 | pass |
| `invalid_transaction_date` | 0 | pass |
| `negative_transaction_amount` | 0 | pass |
| `unexpected_zero_transaction_amount` | 0 | pass |
| `known_zero_transaction_count` | 0 | pass |
| `owner_count_not_one` | 0 | pass |
| `duplicate_account_month_grain` | 0 | pass |
| `customer_360_wrong_grain` | 0 | pass |
| `cohort_rate_out_of_range` | 0 | pass |
| `onboarding_funnel_not_monotonic` | 0 | pass |
| `preloan_feature_leakage` | 0 | pass |

All assertions are designed as zero-row checks: any returned row is a reproducible failure, not a warning hidden in a notebook.
