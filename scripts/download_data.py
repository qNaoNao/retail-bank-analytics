#!/usr/bin/env python3
"""Download Berka data only after the user acknowledges the license caveat."""

from __future__ import annotations

import argparse
import json

from retail_bank_analytics.data_source import OFFICIAL_ARCHIVE_URL, download_and_extract
from retail_bank_analytics.paths import PROJECT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and validate the PKDD'99 Berka archive outside Git."
    )
    parser.add_argument("--url", default=OFFICIAL_ARCHIVE_URL, help="Source archive URL")
    parser.add_argument(
        "--acknowledge-license-caveat",
        action="store_true",
        help="Confirm that docs/DATA_USE_NOTICE.md was read",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.acknowledge_license_caveat:
        print(
            "Download not started. Read docs/DATA_USE_NOTICE.md, then rerun with "
            "--acknowledge-license-caveat."
        )
        return 2

    target = PROJECT_ROOT / "data" / "external" / "berka"
    report = download_and_extract(args.url, target)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
