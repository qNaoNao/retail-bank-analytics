"""Foundation checks that run with Python's standard library."""

from __future__ import annotations

import unittest

from retail_bank_analytics.data_source import OFFICIAL_ARCHIVE_URL, validate_archive_members
from retail_bank_analytics.healthcheck import run_healthcheck
from retail_bank_analytics.paths import PROJECT_ROOT


class FoundationTest(unittest.TestCase):
    def test_healthcheck_is_ok(self) -> None:
        report = run_healthcheck()
        self.assertEqual(report["status"], "ok", report)

    def test_source_uses_https(self) -> None:
        self.assertTrue(OFFICIAL_ARCHIVE_URL.startswith("https://"))

    def test_gitignore_excludes_sensitive_artifacts(self) -> None:
        gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in (".env", "data/external/**", "*.duckdb", "*.key"):
            self.assertIn(pattern, gitignore)

    def test_archive_path_traversal_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_archive_members(["../../outside.txt"])

    def test_normal_archive_members_are_allowed(self) -> None:
        validate_archive_members(["data/account.asc", "data/trans.asc"])


if __name__ == "__main__":
    unittest.main()
