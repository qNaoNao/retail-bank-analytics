"""Create an independent synthetic demo without downloading or redistributing source data."""

import json

from retail_bank_analytics.demo import build_demo
from retail_bank_analytics.paths import PROJECT_ROOT

if __name__ == "__main__":
    print(json.dumps(build_demo(PROJECT_ROOT / "data/processed/demo.duckdb"), indent=2))
