"""Executable data-quality assertions for raw, staging, and mart layers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from retail_bank_analytics.paths import PROJECT_ROOT

ZERO_ROW_ASSERTIONS = {
    "raw_account_row_count": "SELECT 1 WHERE (SELECT COUNT(*) FROM raw.account) <> 4500",
    "raw_transaction_row_count": (
        "SELECT 1 WHERE (SELECT COUNT(*) FROM raw.transactions) <> 1056320"
    ),
    "duplicate_transaction_key": (
        "SELECT transaction_id FROM staging.transactions GROUP BY transaction_id "
        "HAVING COUNT(*) > 1"
    ),
    "orphan_disposition_account": (
        "SELECT d.account_id FROM staging.disposition d LEFT JOIN staging.account a USING "
        "(account_id) WHERE a.account_id IS NULL"
    ),
    "orphan_disposition_client": (
        "SELECT d.client_id FROM staging.disposition d LEFT JOIN staging.client c USING "
        "(client_id) WHERE c.client_id IS NULL"
    ),
    "orphan_transaction_account": (
        "SELECT t.account_id FROM staging.transactions t LEFT JOIN staging.account a USING "
        "(account_id) WHERE a.account_id IS NULL"
    ),
    "orphan_loan_account": (
        "SELECT l.account_id FROM staging.loan l LEFT JOIN staging.account a USING "
        "(account_id) WHERE a.account_id IS NULL"
    ),
    "orphan_card_disposition": (
        "SELECT c.disp_id FROM staging.card c LEFT JOIN staging.disposition d USING (disp_id) "
        "WHERE d.disp_id IS NULL"
    ),
    "invalid_loan_status": (
        "SELECT loan_status_code FROM staging.loan WHERE loan_status_code NOT IN ('A','B','C','D')"
    ),
    "invalid_transaction_direction": (
        "SELECT transaction_type_code FROM staging.transactions WHERE direction NOT IN "
        "('inflow','outflow')"
    ),
    "invalid_transaction_date": (
        "SELECT transaction_id FROM mart.fct_transaction WHERE transaction_date NOT BETWEEN "
        "DATE '1993-01-01' AND DATE '1998-12-31'"
    ),
    "negative_transaction_amount": (
        "SELECT transaction_id FROM mart.fct_transaction WHERE amount < 0"
    ),
    "unexpected_zero_transaction_amount": (
        "SELECT transaction_id FROM mart.fct_transaction WHERE amount = 0 "
        "AND purpose NOT IN ('interest_credit', 'penalty_interest')"
    ),
    "known_zero_transaction_count": (
        "SELECT 1 WHERE (SELECT COUNT(*) FROM mart.fct_transaction WHERE amount = 0) <> 14"
    ),
    "owner_count_not_one": (
        "SELECT account_id FROM mart.bridge_account_client GROUP BY account_id "
        "HAVING COUNT(*) FILTER (WHERE relationship_type = 'owner') <> 1"
    ),
    "duplicate_account_month_grain": (
        "SELECT account_id, month_start FROM mart.account_month GROUP BY 1,2 HAVING COUNT(*) > 1"
    ),
    "customer_360_wrong_grain": (
        "SELECT 1 WHERE (SELECT COUNT(*) FROM mart.customer_360) <> "
        "(SELECT COUNT(*) FROM mart.dim_account) OR "
        "(SELECT COUNT(DISTINCT account_id) FROM mart.customer_360) <> "
        "(SELECT COUNT(*) FROM mart.dim_account)"
    ),
    "cohort_rate_out_of_range": (
        "SELECT * FROM mart.cohort_activity_retention WHERE activity_retention_rate NOT BETWEEN 0 AND 1"
    ),
    "onboarding_funnel_not_monotonic": (
        "SELECT stage_order FROM (SELECT stage_order, accounts, lag(accounts) OVER "
        "(ORDER BY stage_order) AS prior_accounts FROM mart.onboarding_funnel) x "
        "WHERE prior_accounts IS NOT NULL AND accounts > prior_accounts"
    ),
    "preloan_feature_leakage": (
        "SELECT loan_id FROM mart.loan_risk_features WHERE feature_window_end >= loan_date"
    ),
    "lifecycle_unique_grain": (
        "SELECT account_id, month_start FROM mart.account_month_lifecycle "
        "GROUP BY 1,2 HAVING COUNT(*) <> 1"
    ),
    "growth_bridge_reconciles": (
        "SELECT month_start FROM analytics.monthly_growth WHERE "
        "active_accounts <> new_active_accounts + retained_accounts + reactivated_accounts OR "
        "previous_active_accounts <> retained_accounts + newly_inactive_accounts OR "
        "net_active_change <> new_active_accounts + reactivated_accounts - newly_inactive_accounts"
    ),
    "growth_matches_observed_activity": (
        "SELECT g.month_start FROM analytics.monthly_growth g "
        "LEFT JOIN mart.monthly_portfolio p USING(month_start) "
        "WHERE g.active_accounts <> coalesce(p.active_accounts, 0)"
    ),
    "partial_month_excluded": (
        "SELECT l.account_id FROM mart.account_month_lifecycle l "
        "CROSS JOIN analytics.observation_window o WHERE l.month_start > o.last_complete_month"
    ),
    "landmark_unique_grain": (
        "SELECT account_id FROM mart.card_adoption_landmark GROUP BY account_id HAVING COUNT(*) <> 1"
    ),
    "landmark_feature_leakage": (
        "SELECT account_id FROM mart.card_adoption_landmark "
        "WHERE feature_last_transaction_date >= landmark_date"
    ),
    "immature_outcome_is_null": (
        "SELECT account_id FROM mart.card_adoption_landmark "
        "WHERE NOT outcome_observable AND card_adopted_next180d IS NOT NULL"
    ),
    "landmark_outcome_window": (
        "SELECT account_id FROM mart.card_adoption_landmark "
        "WHERE card_adopted_next180d AND (first_card_date < landmark_date "
        "OR first_card_date >= outcome_end_exclusive)"
    ),
}

# Source-specific counts stay mandatory for Berka but are not applied to synthetic fixtures.
BERKA_ONLY_CHECKS = {
    "raw_account_row_count",
    "raw_transaction_row_count",
    "known_zero_transaction_count",
}


def check_connection(
    connection: duckdb.DuckDBPyConnection, *, synthetic: bool = False
) -> dict[str, dict[str, object]]:
    """Run reusable assertions against a caller-owned connection without writing reports."""
    checks = {}
    for name, query in ZERO_ROW_ASSERTIONS.items():
        if synthetic and name in BERKA_ONLY_CHECKS:
            continue
        failures = connection.execute(f"SELECT COUNT(*) FROM ({query}) assertion").fetchone()[0]
        checks[name] = {"failures": failures, "status": "pass" if failures == 0 else "fail"}
    return checks


def run_quality_checks(database_path: Path) -> dict[str, object]:
    """Run every assertion; each query must return zero rows to pass."""

    connection = duckdb.connect(str(database_path), read_only=True)
    checks: dict[str, dict[str, object]] = {}
    try:
        checks = check_connection(connection)
    finally:
        connection.close()

    report = {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "database_path": str(database_path),
        "checks": checks,
        "status": "pass" if all(item["status"] == "pass" for item in checks.values()) else "fail",
    }
    output = PROJECT_ROOT / "data" / "interim" / "quality_report.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def write_quality_markdown(report: dict[str, object], path: Path) -> None:
    lines = [
        "# Data Quality Report",
        "",
        f"Generated: {report['checked_at_utc']}",
        "",
        f"Overall status: **{str(report['status']).upper()}**",
        "",
        "| Assertion | Failed rows | Status |",
        "|---|---:|---|",
    ]
    for name, result in report["checks"].items():
        lines.append(f"| `{name}` | {result['failures']:,} | {result['status']} |")
    lines.extend(
        [
            "",
            "All assertions are designed as zero-row checks: any returned row is a reproducible failure, not a warning hidden in a notebook.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
