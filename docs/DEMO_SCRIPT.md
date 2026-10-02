# Dashboard Demo Script

## 3-minute recruiter walkthrough

1. **Frame the problem (20 seconds):** “I consolidated eight legacy retail-bank tables into a tested customer 360 and decision dashboard. The goal was to demonstrate SQL, modelling, metric governance, and business interpretation rather than another AI wrapper.”
2. **Show trust first (25 seconds):** Mention 1,056,320 transactions, the owner/authorized-user bridge, 20 automated data assertions, and the rule that loan features stop before origination.
3. **Executive overview (30 seconds):** Show portfolio build-out, cash flows, balances, product penetration, and the mature-loan problem rate. State that account growth is portfolio expansion, not causal engagement uplift.
4. **Customer 360 (40 seconds):** Filter a region or segment, compare balance and activity, then drill into one account’s monthly balance. Explain owner-only attribution.
5. **Cohort and funnel (30 seconds):** Show the onboarding product gap and the near-100% activity-retention proxy. Explain why this dataset cannot honestly support churn claims.
6. **Risk (25 seconds):** Compare pre-origination payment burden and balances for repaid versus defaulted finished loans. Emphasize the small default sample and descriptive nature.
7. **Close (10 seconds):** “The recommendations are eligibility reviews, controlled experiments, and back-testing on newer data—not invented business impact.”

## Likely follow-up questions

- Why DuckDB instead of PostgreSQL?
- How did you prevent double counting across clients and accounts?
- What makes the cohort metric a proxy rather than real retention?
- Which SQL uses window functions?
- How did you prevent target leakage in the risk features?
- Which metric would you refuse to put on an executive dashboard, and why?
