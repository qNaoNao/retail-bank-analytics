"""Conservative acquisition helpers for the Berka source data."""

from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

OFFICIAL_ARCHIVE_URL = (
    "https://sorry.vse.cz/~berka/challenge/pkdd1999/data_berka.zip"
)
MIRROR_REPOSITORY_URL = "https://github.com/jlacko/berka-dataset"
MIRROR_COMMIT = "77e9972a1ead107e5f42a91dd989d587bff055a4"
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

SOURCE_SHA256 = {
    "account.asc": "58d7f50abd72e9b1a5568346f74bb54cd71224ee1db9f09a27d7cac563f38cc6",
    "card.asc": "fc669bde6adf6457d87421c0bfb218e9c384a7032c6accd348d207a405e72109",
    "client.asc": "e435c6b92d246f4f0dfd5e2827469d745c06238714c32b3ffb415eebe794e1a7",
    "disp.asc": "ebd801f77b6d322e8ebc08e52f188e7c8fca539325f85f57f8c73434da9d32d8",
    "district.asc": "7f03cf3b9b82f0fdcc3abdf6cc716f145db8e9875c68e2d2e2f7151e9ecf4df3",
    "loan.asc": "68535f609a254aa7a3f03dd8e27dcb822b532df12a0d6046f0666b8dc0b8ae8e",
    "order.asc": "035930fa6acd2ca42a935e654b21e1bb260248f49b6dc6e7de6351b7c4d56d02",
    "trans.asc": "75ab2f39df9d79d79c5c900de90ddd28248b689f214598ac9fa2ff0f574a70d2",
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


def download_mirror_files(target_dir: Path) -> dict[str, object]:
    """Download eight files from a pinned public mirror and verify every checksum."""

    target_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict[str, object]] = {}
    for filename, expected_digest in SOURCE_SHA256.items():
        destination = target_dir / filename
        url = (
            "https://raw.githubusercontent.com/jlacko/berka-dataset/"
            f"{MIRROR_COMMIT}/{filename}"
        )
        if not destination.exists() or sha256(destination) != expected_digest:
            temporary = destination.with_suffix(destination.suffix + ".part")
            request = urllib.request.Request(
                url, headers={"User-Agent": "retail-bank-analytics/0.1"}
            )
            with urllib.request.urlopen(request, timeout=120) as response, temporary.open(
                "wb"
            ) as sink:
                shutil.copyfileobj(response, sink)
            if sha256(temporary) != expected_digest:
                temporary.unlink(missing_ok=True)
                raise ValueError(f"Checksum mismatch for {filename}")
            temporary.replace(destination)
        files[filename] = {
            "bytes": destination.stat().st_size,
            "sha256": sha256(destination),
        }

    report: dict[str, object] = {
        "dataset": "PKDD'99 Czech Financial Dataset (Berka)",
        "mirror_repository": MIRROR_REPOSITORY_URL,
        "mirror_commit": MIRROR_COMMIT,
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "license_note": (
            "Publicly distributed challenge data; no explicit modern redistribution "
            "license was found. Raw files remain local and excluded from Git."
        ),
        "files": files,
    }
    (target_dir / "source_manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


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
