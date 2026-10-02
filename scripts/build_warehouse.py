#!/usr/bin/env python3
"""Build the DuckDB warehouse and fail if a quality assertion fails."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from retail_bank_analytics.paths import PROJECT_ROOT
from retail_bank_analytics.quality import run_quality_checks, write_quality_markdown
from retail_bank_analytics.warehouse import build_warehouse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "retail_bank.duckdb",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_report = build_warehouse(args.database, rebuild=True)
    quality_report = run_quality_checks(args.database)
    write_quality_markdown(quality_report, PROJECT_ROOT / "docs" / "DATA_QUALITY_REPORT.md")
    print(json.dumps(build_report, indent=2))
    print(f"Data quality: {quality_report['status']} ({len(quality_report['checks'])} checks)")
    return 0 if quality_report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
