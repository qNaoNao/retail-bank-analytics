# Growth Decision Memo

Rebuilt from the historical warehouse through **1998-12-31**. Last complete month: 1998-12.

## Decision

Prioritize measurement and a scoped card-offer experiment design. Do not recommend a broad retention campaign from this source: transaction activity is almost universal, closures are absent, and offers / consent are unobserved.

## 1. Explain the active-account change before calling it growth

In 1998-12, 4,478 prior active + 0 first active + 2 reactivated − 56 newly inactive = **4,424 active** (net -54).
Across 1998, there were 0 first-active, 49 reactivation and 108 newly-inactive **events**. The same account can reactivate more than once; annual sums are not unique customers.

The spine includes account-months with no transaction. Only complete calendar months enter the bridge. 'First active' is the first observed customer operation, not necessarily the account-opening month; 'newly inactive' is a monthly transition, not churn.

## 2. Choose a metric that has room to move

The existing 30-day activation stage reaches 4,500/4,500 accounts (100.0%). It is a poor primary experiment endpoint in this sample.
Use a narrower prospective endpoint: first card issuance in days **[180, 360)**, among accounts with no card before day 180. Build behavior features only in **[opening, day 180)**. The cutoff is account-specific, and immature labels stay NULL.
Fully observed candidates: **4,500**; first-card issuances: **179**; rate **3.98%** (95% Wilson interval **3.44%–4.59%**). Excluded for incomplete follow-up: 0; card already issued before landmark: 0. Exclusions can overlap.

| Prior behavior | Candidates | Issued | Rate | 95% Wilson interval | Common-year standardized rate |
|---|---:|---:|---:|---:|---:|
| No outgoing transfer before day 180 | 1,272 | 65 | 5.11% | 4.03%–6.46% | 5.13% |
| Transfer used before day 180 | 3,228 | 114 | 3.53% | 2.95%–4.23% | 3.53% |

The standardized comparison uses the same pooled opening-year weights and only years containing every compared group. This checks composition effects; neither the raw nor standardized rate establishes treatment uplift. Card issuance also does not establish card use or revenue. Confidence intervals do not correct selection bias.

## 3. Check whether an experiment could finish

Planning assumptions: account-level 1:1 randomization, two-sided α=5%, 80% power; independent-proportion normal approximation, no continuity correction or attrition allowance. Traffic of **50 newly eligible accounts/day is an assumption**, not an observed channel metric. The target change is a planning MDE, not an estimated campaign effect.

| Assumed absolute increase | Per arm | Total required | Fits historical pool? | Recruitment + 180-day outcome |
|---|---:|---:|---|---:|
| 0.5 pp | 25,424 | 50,848 | No | ≥1,197 days |
| 1.0 pp | 6,714 | 13,428 | No | ≥449 days |
| 2.0 pp | 1,856 | 3,712 | Yes | ≥255 days |

Historical eligibility is an upper bound: consent, suitability, contactability and current product rules can reduce it. This pool contains cohorts from several years, not simultaneously recruitable traffic. Even 'fits' is only an arithmetic check, not launch approval.

## 4. Pre-register a real test before sending offers

- **Hypothesis:** a consented educational card offer at the landmark increases first-card issuance within the next 180 days by at least the selected MDE.
- **Assignment:** randomize by owner account before exposure; preserve the same assignment on repeat visits; stratify by opening cohort / region if appropriate. Deduplicate owners if future data contains multiple accounts per person.
- **Primary analysis:** intention-to-treat difference in proportions with a two-sided 95% interval after all assigned accounts mature. Include unexposed assigned accounts; report exposure separately.
- **Diagnostics:** check allocation counts / sample-ratio mismatch, cross-arm contamination, event deduplication and missing outcomes before effect estimation. Stop a broken test rather than interpreting its p-value.
- **Guardrails:** complaints / opt-outs, unsuitable offers, operational cost and later credit stress. Current source cannot measure these; instrument them before launch. Issuance alone is insufficient to claim revenue or ROI.
- **Decision:** ship only if the pre-registered practical-effect criterion and guardrails pass; otherwise iterate or stop. No repeated significance peeking or causal claim from observational segments.

## Deliverables

SQL: `sql/marts/080_growth.sql`; dashboard: Growth & experiments; local exports: monthly bridge CSV, cohort/segment CSV, planning JSON and `outputs/growth_report.html`. Regenerate with `make growth-report`.
