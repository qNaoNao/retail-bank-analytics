"""Integration checks against a locally rebuilt warehouse.

The database is intentionally absent from Git, so these tests skip on a source-only clone
and run after `make warehouse` locally.
"""

from __future__ import annotations

import duckdb
import pytest

from retail_bank_analytics.paths import PROJECT_ROOT

DATABASE = PROJECT_ROOT / "data" / "processed" / "retail_bank.duckdb"
pytestmark = pytest.mark.skipif(not DATABASE.exists(), reason="Run `make warehouse` first")


@pytest.fixture(scope="module")
def connection() -> duckdb.DuckDBPyConnection:
    database = duckdb.connect(str(DATABASE), read_only=True)
    yield database
    database.close()


def test_executive_kpi_grain(connection: duckdb.DuckDBPyConnection) -> None:
    customers, accounts, transactions = connection.execute(
        "SELECT customers, accounts, transactions FROM analytics.executive_kpis"
    ).fetchone()
    assert (customers, accounts, transactions) == (4500, 4500, 1_056_320)


def test_cash_flow_reconciles(connection: duckdb.DuckDBPyConnection) -> None:
    inflow, outflow, signed = connection.execute(
        """
        SELECT
            SUM(amount) FILTER (WHERE direction = 'inflow'),
            SUM(amount) FILTER (WHERE direction = 'outflow'),
            SUM(signed_amount)
        FROM mart.fct_transaction
        """
    ).fetchone()
    assert float(inflow - outflow) == pytest.approx(float(signed), abs=0.01)


def test_mature_loan_rate_uses_finished_loans_only(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    mature, problems, rate = connection.execute(
        """
        SELECT COUNT(*), COUNT(*) FILTER (WHERE is_problem), AVG(is_problem::INTEGER)
        FROM mart.fct_loan
        WHERE is_mature
        """
    ).fetchone()
    assert (mature, problems) == (234, 31)
    assert float(rate) == pytest.approx(31 / 234)


def test_onboarding_funnel_is_monotonic(connection: duckdb.DuckDBPyConnection) -> None:
    counts = [
        row[0]
        for row in connection.execute(
            "SELECT accounts FROM mart.onboarding_funnel ORDER BY stage_order"
        ).fetchall()
    ]
    assert counts == sorted(counts, reverse=True)


def test_loan_features_stop_before_origination(connection: duckdb.DuckDBPyConnection) -> None:
    failures = connection.execute(
        """
        SELECT COUNT(*) FROM mart.loan_risk_features
        WHERE feature_window_end >= loan_date
        """
    ).fetchone()[0]
    assert failures == 0
