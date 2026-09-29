"""Central project paths so scripts do not depend on the caller's working directory."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRECTORIES = (
    "app",
    "config",
    "data/external",
    "data/interim",
    "data/processed",
    "docs",
    "notebooks",
    "outputs",
    "scripts",
    "sql/analysis",
    "sql/marts",
    "sql/quality",
    "sql/staging",
    "tests/fixtures",
    "work",
)


def missing_directories() -> list[str]:
    """Return required repository directories that do not exist."""

    return [relative for relative in REQUIRED_DIRECTORIES if not (PROJECT_ROOT / relative).is_dir()]
