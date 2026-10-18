# Metric Dictionary

These are governed definitions implemented in version-controlled SQL and validated by the warehouse quality suite.

| Metric | Grain / definition | Important guardrail |
|---|---|---|
| Customers in executive KPI | Distinct owner-account records in `customer_360` | Owners equal accounts in this source; generalize explicitly for multi-account customers |
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
| First active | Active in month M with no earlier observed active month | First customer operation, not necessarily account opening |
| Retained active | Active in both M−1 and M | Complete calendar months only |
| Reactivated | Active in M, inactive in M−1, active in an earlier month | Monthly activity transition, not a campaign return |
| Newly inactive | Active in M−1, inactive in M | No operation includes absent transaction rows; not confirmed churn |
| Monthly active change | First active + reactivated − newly inactive | Must reconcile to active M minus active M−1 |
| Growth quick ratio | (First active + reactivated) / newly inactive | NULL when the loss denominator is zero; never infinity |
| Day-180 card eligibility | No card issued strictly before opening + 180 days | Analytical candidate definition, not sales suitability / consent |
| Subsequent card issuance rate | First card in [opening+180, opening+360) / eligible accounts with complete follow-up | Exclude incomplete outcomes; do not combine card and loan endpoints |
| Pre-180 segment | Any recorded outgoing bank transfer in [opening, opening+180) vs none | Transaction-channel proxy; no claim that a transfer is digital / online |
| Year-standardized adoption | Sum of within-opening-year rates using common pooled eligibility weights | Only common strata; removes year-mix differences, not causal confounding |
| Rate uncertainty | 95% Wilson score interval from successes and eligible count | Sampling model does not cure selection bias or historical policy effects |
| Experiment MDE | Assumed absolute increase in card-issuance probability | Percentage points, not relative lift or an observed effect |
| Required sample | Two independent proportions, equal allocation, two-sided α=.05, power=.80 | Normal approximation; no continuity / attrition / clustering adjustment |
| Minimum experiment calendar | Ceiling(total required / assumed daily eligibility) + 180 days | Traffic is assumed; historical pool is not simultaneous recruitable traffic |

## Observation clock and filters

`analytics.observation_window` uses the maximum source transaction date, not the current clock. If that date is inside a month, lifecycle reporting stops at the preceding complete month. A global source cutoff assumes the extract covers accounts consistently; it is not a guarantee that every account's upstream feed is complete.

Landmark intervals are half-open: a transaction exactly on day 180 is excluded from features; a first card on day 180 belongs to the outcome; a card on day 360 is outside the outcome. An account needs `outcome_end_exclusive <= as_of_date + 1 day` for its complete outcome. Immature accounts have NULL labels and never enter the rate denominator.

Sidebar lifetime filters apply to Customer 360 and Lending risk. The growth comparison uses only an explicit opening-year filter and pre-landmark behavior; future product holding is not a conditioning variable.

## Segment design principles

- Use explainable, mutually interpretable rules before clustering.
- Base thresholds on documented portfolio quantiles or banking logic.
- Keep “high value,” “high activity,” and “low risk” as separate axes.
- A growth-opportunity segment is a hypothesis for investigation, not a pre-approved sales list.
