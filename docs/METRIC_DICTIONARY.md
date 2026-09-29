# Metric Dictionary — Starter Version

These are governed draft definitions. SQL implementation and validation status will be added in Milestone 4.

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

## Segment design principles

- Use explainable, mutually interpretable rules before clustering.
- Base thresholds on documented portfolio quantiles or banking logic.
- Keep “high value,” “high activity,” and “low risk” as separate axes.
- A growth-opportunity segment is a hypothesis for investigation, not a pre-approved sales list.
