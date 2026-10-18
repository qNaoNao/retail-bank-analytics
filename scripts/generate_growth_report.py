"""Regenerate the growth decision memo, reproducible evidence, and offline HTML report."""

import json

from retail_bank_analytics.growth_report import generate_growth_report
from retail_bank_analytics.paths import PROJECT_ROOT

if __name__ == "__main__":
    print(
        json.dumps(
            generate_growth_report(
                PROJECT_ROOT / "data/processed/retail_bank.duckdb",
                PROJECT_ROOT / "docs/GROWTH_DECISION_MEMO.md",
                PROJECT_ROOT / "outputs",
            ),
            indent=2,
        )
    )
