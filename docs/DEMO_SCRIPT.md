# Dashboard Demo Script

## 3-minute recruiter walkthrough

1. **Frame the question (20 seconds):** “I consolidated eight legacy banking tables to ask where product adoption has room to improve and whether a measured experiment could finish.” Confirm whether the app is showing historical or synthetic data.
2. **Establish trust (20 seconds):** Mention 1,056,320 historical transactions, owner-only money attribution, 28 data assertions, and independent source-free tests.
3. **Find a useful endpoint (25 seconds):** In Cohort & funnel, explain why 100% activation and near-saturated activity retention cannot support a churn story. The data supports product-adoption analysis instead.
4. **Explain change (25 seconds):** Open Growth & experiments. December 1998 reconciles 4,478 prior + 2 reactivated − 56 newly inactive to 4,424 active. A monthly loss is not a confirmed closure.
5. **Define a defensible comparison (30 seconds):** Features stop at day 180; the outcome covers days [180,360). Candidates are card-free with complete follow-up. The historical first-card rate is 179/4,500 = 3.98%, with a 3.44%–4.59% Wilson interval. Show opening-year splits before comparing behavior groups.
6. **Make the decision concrete (40 seconds):** Set the MDE to 1 percentage point: about 13,428 accounts are required, beyond the source pool. At 2 pp, about 3,712 are required; the assumed traffic still implies at least 255 calendar days including outcome maturation. MDE and traffic are assumptions, not observed uplift.
7. **Close (20 seconds):** Outline randomized assignment, intention-to-treat analysis, allocation diagnostics and complaint/suitability guardrails. Open the offline report. Offer Customer 360 and risk drill-downs for technical follow-up.

## Likely follow-up questions

- Why DuckDB instead of PostgreSQL?
- How did you prevent double counting across clients and accounts?
- What makes the cohort metric a proxy rather than real retention?
- Which SQL uses window functions?
- How did you prevent target leakage in the risk features?
- Which metric would you refuse to put on an executive dashboard, and why?
