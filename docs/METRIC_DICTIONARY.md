# Metric Dictionary — Starter Version

These are governed definitions implemented in version-controlled SQL and validated by the warehouse quality suite.

| Metric | Grain / definition | Important guardrail |
|---|---|---|
| Customers | Distinct `client_id` | Do not equate clients with accounts |
| Accounts | Distinct `account_id` | An account may have multiple dispositions |
| Monthly active accounts | Accounts with at least one qualifying transaction in a calendar month | State excluded transaction types, if any |
| Transaction volume | Sum of transaction `amount` for the selected direction/type | Never net credit and debit without an explicit sign rule |
| Net cash flow | Total inflow minus total outflow over the period | This is not profit or income |
| Ending balance | Last observed balance by account and period | Use a deterministic date and transaction ordering |
| Activity retention M+n | Share of opening-cohort accounts active in relative month n | Activity proxy, not confirmed customer retention |
| Card penetration | Eligible/selected accounts with at least one issued card divided by selected accounts | Clarify owner vs authorized-user scope |
| Loan penetration | Selected accounts with a loan divided by selected accounts | At most one loan per account in the source description |
| Mature-loan problem rate | Finished problematic loans divided by finished loans | Exclude still-running loans from a final-outcome rate |
| Amount-weighted problem share | Original amount of finished problematic loans divided by amount of finished loans | Exposure proxy, not realized loss |
| Balance volatility | Within-account standard deviation or coefficient of variation over monthly ending balances | Treat zero/near-zero means explicitly |
| Payment burden | Scheduled monthly loan payment divided by average monthly inflow observed before origination | Null when no valid pre-loan inflow; descriptive, not a policy threshold |
| Funnel activation | Eligible account has a customer-operated transaction within 30 days of opening | Full 12-month observation window required |
| Funnel engagement | Activated account has activity in at least three distinct months in its first six months | Strict subset of activation |
| Funnel product adoption | Engaged account receives a card or loan within 12 months of opening | Product holding is not eligibility or causal conversion |

## Segment design principles

- Use explainable, mutually interpretable rules before clustering.
- Base thresholds on documented portfolio quantiles or banking logic.
- Keep “high value,” “high activity,” and “low risk” as separate axes.
- A growth-opportunity segment is a hypothesis for investigation, not a pre-approved sales list.
