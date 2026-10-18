"""Execute the full SQL pipeline and application in a clean clone, without source data."""

import duckdb
import pytest

from retail_bank_analytics.demo import build_demo
from retail_bank_analytics.paths import PROJECT_ROOT
from retail_bank_analytics.quality import check_connection


@pytest.fixture(scope="module")
def demo_database(tmp_path_factory):
    database = tmp_path_factory.mktemp("synthetic") / "demo.duckdb"
    result = build_demo(database, accounts=32)
    assert result["dataset_kind"] == "synthetic"
    return database


def test_full_source_to_marts_pipeline_runs_without_downloads(demo_database):
    with duckdb.connect(str(demo_database), read_only=True) as connection:
        checks = check_connection(connection, synthetic=True)
        assert all(check["status"] == "pass" for check in checks.values()), checks
        assert connection.execute("SELECT customers FROM analytics.executive_kpis").fetchone() == (
            32,
        )
        assert (
            connection.execute("SELECT count(*) FROM mart.bridge_account_client").fetchone()[0] > 32
        )
        assert connection.execute(
            "SELECT dataset_kind FROM analytics.dataset_metadata"
        ).fetchone() == ("synthetic",)


def test_dashboard_filters_and_growth_controls_on_synthetic_data(demo_database, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("RETAIL_BANK_DATABASE", str(demo_database))
    app = AppTest.from_file(str(PROJECT_ROOT / "app/Home.py"), default_timeout=45).run()
    assert not app.exception
    assert any("Synthetic" in warning.value for warning in app.warning)
    original_required = int(
        next(metric for metric in app.metric if metric.label == "Required total").value.replace(
            ",", ""
        )
    )
    app.number_input[0].set_value(1.0).run()
    assert not app.exception
    new_required = int(
        next(metric for metric in app.metric if metric.label == "Required total").value.replace(
            ",", ""
        )
    )
    assert new_required > original_required
    opening_years = next(control for control in app.multiselect if control.label == "Opening years")
    opening_years.set_value([]).run()
    assert not app.exception
    assert any("No fully observed" in info.value for info in app.info)
    app.sidebar.multiselect[0].set_value([]).run()
    assert not app.exception
    assert any("No accounts match" in warning.value for warning in app.warning)
    # Empty customer selection must never silently display all historical loans.
    loan_metric = next(metric for metric in app.metric if metric.label == "Selected loans")
    assert loan_metric.value == "0"
    assert any("Growth" in tab.label for tab in app.tabs)


def test_synthetic_data_cannot_overwrite_historical_findings(demo_database, tmp_path):
    from retail_bank_analytics.growth_report import generate_growth_report

    report = tmp_path / "historical_findings.md"
    report.write_text("keep previous historical findings")
    with pytest.raises(ValueError, match="cannot be generated from synthetic"):
        generate_growth_report(demo_database, report, tmp_path / "outputs")
    assert report.read_text() == "keep previous historical findings"
