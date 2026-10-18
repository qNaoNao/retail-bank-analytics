"""A failed rebuild must preserve the last usable analytical database."""

import duckdb
import pytest

from retail_bank_analytics import warehouse


def test_failed_rebuild_preserves_previous_database(tmp_path, monkeypatch):
    database = tmp_path / "published.duckdb"
    with duckdb.connect(str(database)) as connection:
        connection.execute("CREATE TABLE marker AS SELECT 42 AS value")
    monkeypatch.setattr(warehouse, "find_source_dir", lambda: tmp_path)

    def fail_before_loading(connection, source):
        raise ValueError("deliberate source failure")

    monkeypatch.setattr(warehouse, "load_raw_tables", fail_before_loading)
    with pytest.raises(ValueError, match="deliberate source failure"):
        warehouse.build_warehouse(database)
    with duckdb.connect(str(database), read_only=True) as connection:
        assert connection.execute("SELECT value FROM marker").fetchone() == (42,)
    assert not list(tmp_path.glob(".warehouse-*"))
