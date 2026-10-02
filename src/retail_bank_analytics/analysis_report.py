"""Generate an evidence-backed business findings report from DuckDB marts."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb


def _scalar(connection: duckdb.DuckDBPyConnection, query: str) -> float | int:
    return connection.execute(query).fetchone()[0]


def generate_analysis_report(database_path: Path, markdown_path: Path, json_path: Path) -> None:
    connection = duckdb.connect(str(database_path), read_only=True)
    try:
        kpi = connection.execute("SELECT * FROM analytics.executive_kpis").fetchdf().iloc[0]
        segments = connection.execute(
            "SELECT * FROM analytics.segment_summary ORDER BY customer_count DESC"
        ).fetchdf()
        product = connection.execute(
            """
            SELECT (card_count > 0) AS has_card, (loan_count > 0) AS has_loan,
                   COUNT(*) AS accounts
            FROM mart.account_360 GROUP BY 1, 2 ORDER BY 1, 2
            """
        ).fetchdf()
        funnel = connection.execute(
            "SELECT * FROM mart.onboarding_funnel ORDER BY stage_order"
        ).fetchdf()
        risk = connection.execute(
            """
            SELECT loan_status, COUNT(*) AS loans, AVG(loan_amount) AS average_loan_amount,
                   AVG(payment_to_monthly_inflow) AS average_payment_burden,
                   AVG((preloan_minimum_balance < 0)::INTEGER) AS negative_balance_share
            FROM mart.loan_risk_features
            WHERE is_mature
            GROUP BY loan_status
            """
        ).fetchdf()
        cohort_12 = _scalar(
            connection,
            """
            SELECT SUM(active_accounts)::DOUBLE / SUM(observable_accounts)
            FROM mart.cohort_activity_retention WHERE months_since_open = 12
            """,
        )
        first_year_active = _scalar(
            connection,
            "SELECT AVG(active_accounts) FROM mart.monthly_portfolio WHERE year(month_start)=1993",
        )
        final_year_active = _scalar(
            connection,
            "SELECT AVG(active_accounts) FROM mart.monthly_portfolio WHERE year(month_start)=1998",
        )
        ever_negative = _scalar(
            connection,
            "SELECT COUNT(*) FROM mart.account_360 WHERE minimum_observed_balance < 0",
        )
    finally:
        connection.close()

    product_lookup = {
        (bool(row.has_card), bool(row.has_loan)): int(row.accounts)
        for row in product.itertuples(index=False)
    }
    risk_lookup = {row.loan_status: row for row in risk.itertuples(index=False)}
    defaulted = risk_lookup["defaulted"]
    repaid = risk_lookup["repaid"]
    adopted = int(funnel.iloc[-1]["accounts"])
    eligible = int(funnel.iloc[0]["accounts"])

    evidence = {
        "customers": int(kpi.customers),
        "accounts": int(kpi.accounts),
        "transactions": int(kpi.transactions),
        "total_inflow": float(kpi.total_inflow),
        "total_outflow": float(kpi.total_outflow),
        "average_month_end_balance": float(kpi.average_month_end_balance),
        "card_penetration": float(kpi.card_penetration),
        "loan_penetration": float(kpi.loan_penetration),
        "mature_loan_problem_rate": float(kpi.mature_loan_problem_rate),
        "twelve_month_activity_retention": float(cohort_12),
        "first_year_average_active_accounts": float(first_year_active),
        "final_year_average_active_accounts": float(final_year_active),
        "accounts_ever_negative": int(ever_negative),
        "no_card_no_loan_accounts": product_lookup[(False, False)],
        "card_only_accounts": product_lookup[(True, False)],
        "loan_only_accounts": product_lookup[(False, True)],
        "card_and_loan_accounts": product_lookup[(True, True)],
        "onboarding_eligible_accounts": eligible,
        "product_adopted_within_12m": adopted,
        "defaulted_average_loan_amount": float(defaulted.average_loan_amount),
        "repaid_average_loan_amount": float(repaid.average_loan_amount),
        "defaulted_average_payment_burden": float(defaulted.average_payment_burden),
        "repaid_average_payment_burden": float(repaid.average_payment_burden),
        "defaulted_negative_balance_share": float(defaulted.negative_balance_share),
        "repaid_negative_balance_share": float(repaid.negative_balance_share),
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    segment_rows = []
    for row in segments.itertuples(index=False):
        segment_rows.append(
            f"| `{row.behavior_segment}` | {row.customer_count:,} | "
            f"{row.average_month_end_balance:,.0f} | {row.card_penetration:.1%} | "
            f"{row.loan_penetration:.1%} | {row.loan_customer_count:,} |"
        )

    lines = [
        "# Analysis Findings",
        "",
        "All amounts are historical Czech koruna (CZK). Findings are descriptive associations, not causal effects.",
        "",
        "## Executive portfolio",
        "",
        f"- The analytical layer covers **{evidence['customers']:,} customers**, **{evidence['accounts']:,} accounts**, and **{evidence['transactions']:,} transactions**.",
        f"- Recorded inflow is **CZK {evidence['total_inflow']/1_000_000:,.1f} million** and outflow is **CZK {evidence['total_outflow']/1_000_000:,.1f} million**.",
        f"- Average monthly ending balance is **CZK {evidence['average_month_end_balance']:,.0f}**; **{evidence['accounts_ever_negative']:,} accounts ({evidence['accounts_ever_negative']/evidence['accounts']:.1%})** went below zero at least once.",
        f"- Average monthly active accounts rose from **{evidence['first_year_average_active_accounts']:,.0f} in 1993** to **{evidence['final_year_average_active_accounts']:,.0f} in 1998**. This mainly reflects portfolio build-out, not proven same-customer engagement growth.",
        "",
        "## Customer value and product engagement",
        "",
        "| Behaviour segment | Customers | Avg. month-end balance | Card penetration | Loan penetration | Loan customers |",
        "|---|---:|---:|---:|---:|---:|",
        *segment_rows,
        "",
        f"- **{evidence['no_card_no_loan_accounts']:,} accounts ({evidence['no_card_no_loan_accounts']/evidence['accounts']:.1%})** have neither a card nor loan; {evidence['card_only_accounts']:,} are card-only, {evidence['loan_only_accounts']:,} are loan-only, and {evidence['card_and_loan_accounts']:,} hold both.",
        f"- Among accounts with a full 12-month observation window, **{adopted:,} of {eligible:,} ({adopted/eligible:.1%})** reached the conjunctive funnel stage of early activation, sustained six-month engagement, and card-or-loan adoption within 12 months.",
        "- This identifies a product-adoption gap for investigation. It does not prove eligibility, propensity, or treatment uplift; those require policy filters and an experiment.",
        "",
        "## Cohort and retention limitation",
        "",
        f"- Weighted 12-month customer-operation activity retention is **{cohort_12:.1%}**. The near-saturated rate provides little churn discrimination.",
        "- The defensible conclusion is that the dataset supports opening-cohort engagement and balance trajectories, but **not true churn modelling**, because account closure and customer-exit labels are absent.",
        "",
        "## Lending risk",
        "",
        f"- Of 234 finished loans, 31 defaulted: a mature-loan problem rate of **{evidence['mature_loan_problem_rate']:.2%}**.",
        f"- Defaulted loans averaged **CZK {evidence['defaulted_average_loan_amount']:,.0f}**, versus **CZK {evidence['repaid_average_loan_amount']:,.0f}** for repaid loans.",
        f"- Average scheduled-payment-to-pre-loan-monthly-inflow was **{evidence['defaulted_average_payment_burden']:.1%}** for defaulted loans and **{evidence['repaid_average_payment_burden']:.1%}** for repaid loans.",
        f"- **{evidence['defaulted_negative_balance_share']:.1%}** of defaulted borrowers had a negative balance before origination versus **{evidence['repaid_negative_balance_share']:.1%}** of repaid borrowers in this sample.",
        "- These pre-origination associations support further underwriting/back-testing analysis. They are not a modern credit policy, and the sample contains only 31 defaults.",
        "",
        "## Recommended actions",
        "",
        "1. Review high-value segments for product eligibility, then validate offers with a controlled campaign rather than treating descriptive penetration gaps as uplift.",
        "2. Separate account activation from product adoption in management reporting; activity is nearly universal, while 12-month product adoption is selective.",
        "3. Back-test payment burden and pre-loan negative-balance flags as transparent risk indicators on newer, policy-representative data.",
        "4. Do not build a churn model from this source. Acquire closure/contact data before making retention claims.",
        "",
        "## Interpretation boundaries",
        "",
        "- Historical 1990s behaviour is not current market sizing.",
        "- Full-lifetime customer segments must not be used as origination-time risk predictors.",
        "- Regional and segment risk rates can be unstable where loan counts are small.",
        "- A recommendation is a proposed next action; it is not an observed business impact.",
        "",
    ]
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
