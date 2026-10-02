"""Streamlit smoke test for the locally rebuilt dashboard."""

from __future__ import annotations

import pytest

from retail_bank_analytics.paths import PROJECT_ROOT

DATABASE = PROJECT_ROOT / "data" / "processed" / "retail_bank.duckdb"
pytestmark = pytest.mark.skipif(not DATABASE.exists(), reason="Run `make warehouse` first")


def test_dashboard_renders_without_exception() -> None:
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30)
    app.run()
    assert not app.exception
    assert app.title[0].value == "Retail Bank Customer 360"
