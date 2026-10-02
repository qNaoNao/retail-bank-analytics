"""Build the local DuckDB analytical warehouse from audited source files."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from retail_bank_analytics.paths import PROJECT_ROOT
from retail_bank_analytics.source_contract import SOURCE_CONTRACTS

RAW_TABLE_NAMES = {
    "account": "account",
    "card": "card",
    "client": "client",
    "disp": "disposition",
    "district": "district",
    "loan": "loan",
    "order": "orders",
    "trans": "transactions",
}

SQL_LAYERS = (
    "sql/staging/010_staging.sql",
    "sql/marts/020_core_model.sql",
    "sql/marts/030_account_month.sql",
    "sql/marts/040_customer_360.sql",
    "sql/marts/050_cohort.sql",
    "sql/marts/060_loan_risk.sql",
    "sql/analysis/070_portfolio_views.sql",
)


def find_source_dir() -> Path:
    """Return the first local source directory containing all eight tables."""

    candidates = (
        PROJECT_ROOT / "data" / "external" / "berka",
        PROJECT_ROOT / "data" / "external" / "berka-mirror",
    )
    expected = {contract.filename for contract in SOURCE_CONTRACTS.values()}
    for candidate in candidates:
        if expected.issubset({path.name for path in candidate.glob("*.asc")}):
            return candidate
    raise FileNotFoundError("Berka source files not found. Run `make download-data` first.")


def load_raw_tables(connection: duckdb.DuckDBPyConnection, source_dir: Path) -> None:
    """Load source columns as strings so staging decisions remain explicit."""

    connection.execute("CREATE SCHEMA IF NOT EXISTS raw")
    for source_name, contract in SOURCE_CONTRACTS.items():
        table_name = RAW_TABLE_NAMES[source_name]
        escaped_path = str(source_dir / contract.filename).replace("'", "''")
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE raw.{table_name} AS
            SELECT *
            FROM read_csv(
                '{escaped_path}',
                delim = ';',
                header = true,
                all_varchar = true,
                nullstr = ''
            )
            """
        )


def execute_sql_layers(connection: duckdb.DuckDBPyConnection) -> list[str]:
    """Execute ordered, version-controlled SQL transformation layers."""

    executed: list[str] = []
    for relative_path in SQL_LAYERS:
        path = PROJECT_ROOT / relative_path
        connection.execute(path.read_text(encoding="utf-8"))
        executed.append(relative_path)
    return executed


def build_warehouse(database_path: Path, rebuild: bool = True) -> dict[str, object]:
    """Build all warehouse layers and return reproducibility metadata."""

    source_dir = find_source_dir()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if rebuild and database_path.exists():
        database_path.unlink()

    connection = duckdb.connect(str(database_path))
    try:
        connection.execute("SET threads = 4")
        load_raw_tables(connection, source_dir)
        executed = execute_sql_layers(connection)
        connection.execute("CHECKPOINT")
        schemas = connection.execute(
            """
            SELECT table_schema, COUNT(*) AS table_count
            FROM information_schema.tables
            WHERE table_schema IN ('raw', 'staging', 'mart', 'analytics')
            GROUP BY table_schema
            ORDER BY table_schema
            """
        ).fetchall()
    finally:
        connection.close()

    report = {
        "built_at_utc": datetime.now(UTC).isoformat(),
        "database_path": str(database_path),
        "database_bytes": database_path.stat().st_size,
        "source_dir": str(source_dir),
        "sql_layers": executed,
        "tables_by_schema": {schema: count for schema, count in schemas},
    }
    report_path = PROJECT_ROOT / "data" / "interim" / "warehouse_build.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
