"""Conservative acquisition helpers for the Berka source archive."""

from __future__ import annotations

import hashlib
import shutil
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


OFFICIAL_ARCHIVE_URL = (
    "https://sorry.vse.cz/~berka/challenge/pkdd1999/data_berka.zip"
)
EXPECTED_TABLES = {
    "account.asc",
    "card.asc",
    "client.asc",
    "disp.asc",
    "district.asc",
    "loan.asc",
    "order.asc",
    "trans.asc",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive_members(members: list[str]) -> None:
    """Reject absolute paths and parent traversal before archive extraction."""

    for member in members:
        path = PurePosixPath(member)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Unsafe archive member: {member}")


def download_and_extract(url: str, target_dir: Path) -> dict[str, object]:
    """Download the source archive, extract safely, and report inventory metadata."""

    target_dir.mkdir(parents=True, exist_ok=True)
    archive_path = target_dir / "data_berka.zip"
    request = urllib.request.Request(url, headers={"User-Agent": "retail-bank-analytics/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response, archive_path.open("wb") as sink:
        shutil.copyfileobj(response, sink)

    with zipfile.ZipFile(archive_path) as archive:
        validate_archive_members(archive.namelist())
        archive.extractall(target_dir)

    actual_tables = {
        path.name.lower()
        for path in target_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".asc"
    }
    missing = sorted(EXPECTED_TABLES - actual_tables)
    if missing:
        raise ValueError(f"Archive is missing expected source tables: {missing}")

    return {
        "url": url,
        "archive": str(archive_path),
        "bytes": archive_path.stat().st_size,
        "sha256": sha256(archive_path),
        "tables": sorted(actual_tables),
    }
