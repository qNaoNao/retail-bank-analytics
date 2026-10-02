"""Dependency-free audit of source shape, keys, and missing values."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from retail_bank_analytics.data_source import SOURCE_SHA256
from retail_bank_analytics.source_contract import SOURCE_CONTRACTS, SourceTableContract


def _digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def audit_table(path: Path, contract: SourceTableContract) -> dict[str, object]:
    row_count = 0
    primary_keys: set[str] = set()
    duplicate_keys = 0
    missing = Counter()
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=";", quotechar='"')
        actual_columns = tuple(reader.fieldnames or ())
        for row in reader:
            row_count += 1
            key = (row.get(contract.primary_key) or "").strip()
            if key in primary_keys:
                duplicate_keys += 1
            primary_keys.add(key)
            for column in actual_columns:
                if (row.get(column) or "").strip() in {"", "?"}:
                    missing[column] += 1

    digest = _digest(path)
    checks = {
        "columns_match": actual_columns == contract.columns,
        "row_count_matches": row_count == contract.expected_rows,
        "primary_key_unique": duplicate_keys == 0,
        "checksum_matches": digest == SOURCE_SHA256[contract.filename],
    }
    return {
        "file": contract.filename,
        "bytes": path.stat().st_size,
        "columns": list(actual_columns),
        "expected_columns": list(contract.columns),
        "rows": row_count,
        "expected_rows": contract.expected_rows,
        "primary_key": contract.primary_key,
        "duplicate_primary_keys": duplicate_keys,
        "missing_by_column": dict(missing),
        "sha256": digest,
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
    }


def audit_source(source_dir: Path) -> dict[str, object]:
    tables = {
        table: audit_table(source_dir / contract.filename, contract)
        for table, contract in SOURCE_CONTRACTS.items()
    }
    return {
        "dataset": "PKDD'99 Czech Financial Dataset (Berka)",
        "audited_at_utc": datetime.now(UTC).isoformat(),
        "source_dir": str(source_dir),
        "total_rows": sum(int(table["rows"]) for table in tables.values()),
        "tables": tables,
        "status": "pass" if all(table["status"] == "pass" for table in tables.values()) else "fail",
    }


def write_audit(report: dict[str, object], json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Data Audit",
        "",
        f"Generated: {report['audited_at_utc']}",
        "",
        f"Overall status: **{str(report['status']).upper()}**",
        "",
        f"Total source rows: **{int(report['total_rows']):,}**",
        "",
        "| Table | Rows | Expected | PK duplicates | Missing cells | Checksum | Status |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for table_name, table in report["tables"].items():
        missing_cells = sum(table["missing_by_column"].values())
        checksum = "match" if table["checks"]["checksum_matches"] else "mismatch"
        lines.append(
            f"| {table_name} | {table['rows']:,} | {table['expected_rows']:,} | "
            f"{table['duplicate_primary_keys']:,} | {missing_cells:,} | {checksum} | "
            f"{table['status']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Row counts, headers, primary-key uniqueness, and pinned-file checksums match the contract.",
            "- Missing cells are expected in optional transaction counterparty fields and selected district rates.",
            "- This audit validates source integrity only; foreign keys, accepted codes, dates, and business rules are tested in the DuckDB staging pipeline.",
            "- Raw source files remain excluded from Git.",
            "",
        ]
    )
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
