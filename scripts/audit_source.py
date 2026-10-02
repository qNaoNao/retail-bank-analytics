#!/usr/bin/env python3
"""Audit downloaded Berka source files against their data contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from retail_bank_analytics.paths import PROJECT_ROOT
from retail_bank_analytics.source_audit import audit_source, write_audit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=str,
        default=str(PROJECT_ROOT / "data" / "external" / "berka"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir)
    if not source_dir.is_absolute():
        source_dir = PROJECT_ROOT / source_dir
    report = audit_source(source_dir)
    write_audit(
        report,
        PROJECT_ROOT / "data" / "interim" / "source_audit.json",
        PROJECT_ROOT / "docs" / "SOURCE_AUDIT.md",
    )
    print(f"Source audit: {report['status']} ({report['total_rows']:,} rows)")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
