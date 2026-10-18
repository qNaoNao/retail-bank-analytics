"""Small hand-calculated histories exercise gaps, censoring and exact window edges."""

from datetime import date, timedelta

import duckdb
import pytest

from retail_bank_analytics.paths import PROJECT_ROOT


@pytest.fixture
def growth_connection():
    with duckdb.connect() as connection:
        connection.execute("CREATE SCHEMA mart; CREATE SCHEMA analytics")
        connection.execute(
            "CREATE TABLE mart.dim_account(account_id INT, opened_date DATE, district_id INT)"
        )
        connection.execute(
            "INSERT INTO mart.dim_account VALUES (1,'1998-01-01',1),(2,'1998-01-01',1),(3,'1998-11-01',1),(4,'1998-01-01',1),(5,'1998-01-01',1)"
        )
        connection.execute("CREATE TABLE mart.dim_district(district_id INT, region_name VARCHAR)")
        connection.execute("INSERT INTO mart.dim_district VALUES (1,'Test region')")
        connection.execute(
            "CREATE TABLE mart.account_month(account_id INT, month_start DATE, customer_transaction_count INT)"
        )
        connection.execute(
            "INSERT INTO mart.account_month VALUES (1,'1998-01-01',1),(1,'1998-03-01',1),(2,'1998-01-01',1),(2,'1998-02-01',1),(3,'1998-11-01',1),(1,'1998-12-01',1)"
        )
        connection.execute(
            "CREATE TABLE mart.fct_transaction(transaction_id INT, account_id INT, transaction_date DATE, operation_code VARCHAR, operation VARCHAR, balance_after_transaction DOUBLE)"
        )
        opening = date(1998, 1, 1)
        for i, offset in enumerate((0, 179, 180, 359, 360)):
            connection.execute(
                "INSERT INTO mart.fct_transaction VALUES (?,?,?,'X','bank_transfer_out',?)",
                [i + 1, 1, opening + timedelta(days=offset), 100 if offset < 180 else 999999],
            )
        connection.execute("CREATE TABLE mart.fct_card(account_id INT, issued_date DATE)")
        for account, offset in ((1, 180), (2, 179), (4, 360), (5, 359)):
            connection.execute(
                "INSERT INTO mart.fct_card VALUES (?,?)",
                [account, opening + timedelta(days=offset)],
            )
        connection.execute((PROJECT_ROOT / "sql/marts/080_growth.sql").read_text())
        yield connection


def test_missing_month_and_return_are_not_dropped(growth_connection):
    rows = growth_connection.execute(
        "SELECT month_start,lifecycle_state,became_inactive FROM mart.account_month_lifecycle WHERE account_id=1 ORDER BY month_start LIMIT 3"
    ).fetchall()
    assert rows == [
        (date(1998, 1, 1), "new", False),
        (date(1998, 2, 1), "inactive", True),
        (date(1998, 3, 1), "reactivated", False),
    ]


def test_growth_bridge_matches_hand_calculation(growth_connection):
    assert growth_connection.execute(
        "SELECT active_accounts,previous_active_accounts,new_active_accounts,retained_accounts,reactivated_accounts,newly_inactive_accounts,net_active_change FROM analytics.monthly_growth WHERE month_start='1998-02-01'"
    ).fetchone() == (1, 2, 0, 1, 0, 1, -1)
    assert growth_connection.execute(
        "SELECT active_accounts,reactivated_accounts,newly_inactive_accounts,net_active_change FROM analytics.monthly_growth WHERE month_start='1998-03-01'"
    ).fetchone() == (1, 1, 1, 0)


def test_partial_last_month_is_excluded(growth_connection):
    assert growth_connection.execute(
        "SELECT max(month_start) FROM analytics.monthly_growth"
    ).fetchone()[0] == date(1998, 11, 1)


def test_features_exclude_landmark_day_and_later(growth_connection):
    count, balance, last, cutoff = growth_connection.execute(
        "SELECT pre180_transaction_count,pre180_last_balance,feature_last_transaction_date,landmark_date FROM mart.card_adoption_landmark WHERE account_id=1"
    ).fetchone()
    assert count == 2
    assert balance == 100
    assert last < cutoff


def test_card_eligibility_and_outcome_boundaries(growth_connection):
    rows = growth_connection.execute(
        "SELECT account_id,card_free_at_landmark,card_adopted_next180d FROM mart.card_adoption_landmark WHERE account_id IN (1,2,4,5) ORDER BY 1"
    ).fetchall()
    assert rows == [(1, True, True), (2, False, False), (4, True, False), (5, True, True)]


def test_immature_accounts_are_null_not_nonconverters(growth_connection):
    assert growth_connection.execute(
        "SELECT outcome_observable,card_adopted_next180d FROM mart.card_adoption_landmark WHERE account_id=3"
    ).fetchone() == (False, None)
    assert growth_connection.execute(
        "SELECT sum(eligible_accounts),sum(adopted_accounts) FROM analytics.card_adoption_segments"
    ).fetchone() == (3, 2)
