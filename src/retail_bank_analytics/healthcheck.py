"""Dependency-free project health check used before the Conda environment exists."""

from __future__ import annotations

import json
import platform

from retail_bank_analytics import __version__
from retail_bank_analytics.paths import PROJECT_ROOT, missing_directories


REQUIRED_FILES = (
    ".gitignore",
    "environment.yml",
    "pyproject.toml",
    "README.md",
    "PROJECT_SPEC.md",
    "ROADMAP.md",
    "DECISIONS.md",
    "STATUS.md",
)


def run_healthcheck() -> dict[str, object]:
    """Return a small machine-readable report and never mutate the repository."""

    missing_files = [name for name in REQUIRED_FILES if not (PROJECT_ROOT / name).is_file()]
    missing_dirs = missing_directories()
    return {
        "project": "retail-bank-analytics",
        "package_version": __version__,
        "python": platform.python_version(),
        "project_root": str(PROJECT_ROOT),
        "missing_files": missing_files,
        "missing_directories": missing_dirs,
        "status": "ok" if not missing_files and not missing_dirs else "failed",
    }


def main() -> int:
    report = run_healthcheck()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
