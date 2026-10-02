#!/usr/bin/env python3
"""Regenerate the business findings document from tested DuckDB marts."""

from retail_bank_analytics.analysis_report import generate_analysis_report
from retail_bank_analytics.paths import PROJECT_ROOT


def main() -> int:
    generate_analysis_report(
        PROJECT_ROOT / "data" / "processed" / "retail_bank.duckdb",
        PROJECT_ROOT / "docs" / "ANALYSIS_FINDINGS.md",
        PROJECT_ROOT / "outputs" / "analysis_summary.json",
    )
    print("Generated docs/ANALYSIS_FINDINGS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
