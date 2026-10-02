# Analytical Data Model

The warehouse separates source fidelity from business usability. Raw values remain unchanged, staging performs explicit casting and translation, and marts expose stable grains for analysis and the dashboard.

```mermaid
flowchart LR
    subgraph Raw[raw — source fidelity]
        RA[account]
        RC[client]
        RD[disposition]
        RT[transactions]
        RL[loan]
        RK[card]
        RO[orders]
        RG[district]
    end

    subgraph Staging[staging — typed and translated]
        SA[account]
        SC[client]
        SD[disposition]
        ST[transactions]
        SL[loan]
    end

    subgraph Core[mart — dimensions and facts]
        DA[dim_account]
        DC[dim_client]
        BR[bridge_account_client]
        FT[fct_transaction]
        FL[fct_loan]
        FC[fct_card]
    end

    subgraph Products[mart — analytical products]
        AM[account_month]
        C360[customer_360]
        CO[cohort engagement]
        FU[onboarding funnel]
        LR[loan risk features]
    end

    Raw --> Staging --> Core --> Products
    DA --> BR
    DC --> BR
    FT --> AM --> C360
    FL --> LR
    FC --> C360
```

## Grains and keys

| Object | Grain | Key / guardrail |
|---|---|---|
| `raw.*` | One row per source record | All columns retained as strings |
| `staging.transactions` | One transaction | `transaction_id`; positive amount plus derived signed amount |
| `bridge_account_client` | One account-client permission | Owner and authorized user remain distinct |
| `account_month` | One account-observed month | Deterministic ending balance uses date and transaction ID ordering |
| `account_360` | One account | Product and lifetime metrics; no client attribution yet |
| `customer_360` | One account owner | Owner-only money attribution prevents joint-access double counting |
| `cohort_activity_retention` | One opening cohort-relative month | Customer-operation activity proxy, not confirmed retention |
| `onboarding_funnel` | One conjunctive stage | Every later stage is a strict subset of the prior stage |
| `loan_risk_features` | One loan | Transaction features end strictly before loan origination |

## Code translation policy

Original Czech codes remain in `*_code` fields. English labels are additional fields, never destructive replacements. This makes the analysis readable while retaining a traceable path to the source.

## Why the bridge matters

The dataset contains 4,500 account owners and 869 authorized users. Joining transactions directly through every disposition would duplicate account balances and cash flow. Portfolio money metrics therefore stay at account grain; customer 360 assigns them only to the `owner` relationship. Authorized-user behaviour can be analysed separately without corrupting totals.
