#!/usr/bin/env python3
"""Run the project health check without requiring third-party dependencies."""

from retail_bank_analytics.healthcheck import main


if __name__ == "__main__":
    raise SystemExit(main())
