"""Deterministic, independently generated banking fixtures for a source-only demo.

No historical rows, distributions or customer identifiers are copied from Berka.
Synthetic results demonstrate behavior and must never be presented as project findings.
"""

from __future__ import annotations

import calendar
import random
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb

from retail_bank_analytics.quality import check_connection
from retail_bank_analytics.source_contract import SOURCE_CONTRACTS
from retail_bank_analytics.warehouse import RAW_TABLE_NAMES, execute_sql_layers


def seed_synthetic_raw(connection: duckdb.DuckDBPyConnection, accounts: int = 240) -> None:
    """Seed eight raw tables with explicit synthetic ownership and event histories."""
    if accounts < 24:
        raise ValueError("Use at least 24 synthetic accounts to exercise all dashboard states")
    rng = random.Random(31997)
    rows: dict[str, list[tuple]] = {name: [] for name in SOURCE_CONTRACTS}
    for district in range(1, 5):
        rows["district"].append(
            (
                district,
                f"Demo district {district}",
                f"Demo region {district}",
                100000,
                10,
                10,
                5,
                1,
                3,
                60,
                9000,
                3.5,
                4,
                100,
                250,
                300,
            )
        )
    transaction_id = 1
    for i in range(accounts):
        account_id = 100001 + i
        owner_id = 200001 + i
        disp_id = 300001 + i
        district = i % 4 + 1
        opened = date(1995, 1, 1) + timedelta(days=(i * 13) % 1360)
        rows["account"].append(
            (account_id, district, "POPLATEK MESICNE", opened.strftime("%y%m%d"))
        )
        rows["client"].append((owner_id, "605115" if i % 2 else "600115", district))
        rows["disp"].append((disp_id, owner_id, account_id, "OWNER"))
        if i % 7 == 0:
            authorized_id = 500001 + i
            rows["client"].append((authorized_id, "650215", district))
            rows["disp"].append((600001 + i, authorized_id, account_id, "DISPONENT"))
        card_date = opened + timedelta(days=90 if i % 13 == 0 else 210 + i % 250)
        if i % 3 == 0 and card_date <= date(1998, 12, 31):
            rows["card"].append(
                (400001 + i, disp_id, "classic", card_date.strftime("%y%m%d 00:00:00"))
            )
        loan_date = opened + timedelta(days=240)
        if i % 5 == 0 and loan_date <= date(1998, 12, 31):
            status = ("A", "B", "C", "D")[(i // 5) % 4]
            rows["loan"].append(
                (700001 + i, account_id, loan_date.strftime("%y%m%d"), 48000, 24, 2000, status)
            )
        rows["order"].append((800001 + i, account_id, "DEMO", "SYNTHETIC", 500, "SIPO"))
        balance = 1500.0 + i * 100
        month = opened.replace(day=1)
        age = 0
        while month <= date(1998, 12, 1):
            last = month.replace(day=calendar.monthrange(month.year, month.month)[1])
            # Fees/interest survive gaps so a sparse observed-month table cannot hide inactivity.
            events = [(last, "PRIJEM", "", 5.0, "UROK")]
            active = age == 0 or ((i + age) % 6 != 0 and not (i % 11 == 0 and age > 6))
            if active:
                day = max(opened, month + timedelta(days=5))
                events += [
                    (day, "PRIJEM", "VKLAD", 3000.0 + rng.randint(0, 2000), ""),
                    (
                        min(last, day + timedelta(days=4)),
                        "VYDAJ",
                        "PREVOD NA UCET" if i % 2 else "VYBER",
                        2000.0,
                        "SIPO",
                    ),
                ]
            for event_date, direction, operation, amount, purpose in sorted(events):
                balance += amount if direction == "PRIJEM" else -amount
                rows["trans"].append(
                    (
                        transaction_id,
                        account_id,
                        event_date.strftime("%y%m%d"),
                        direction,
                        operation,
                        amount,
                        round(balance, 2),
                        purpose,
                        "",
                        "",
                    )
                )
                transaction_id += 1
            month = date(month.year + (month.month == 12), month.month % 12 + 1, 1)
            age += 1
    connection.execute("CREATE SCHEMA raw")
    for name, contract in SOURCE_CONTRACTS.items():
        columns = ", ".join(f'"{column}" VARCHAR' for column in contract.columns)
        table = RAW_TABLE_NAMES[name]
        connection.execute(f"CREATE TABLE raw.{table} ({columns})")
        if rows[name]:
            placeholders = ", ".join("?" for _ in contract.columns)
            # Empty strings are NULL in the real CSV loader too.
            values = [tuple(None if str(v) == "" else str(v) for v in row) for row in rows[name]]
            connection.executemany(f"INSERT INTO raw.{table} VALUES ({placeholders})", values)


def build_demo(database_path: Path, accounts: int = 240) -> dict[str, object]:
    """Build a separate demo database, checking it before replacing an earlier demo."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".demo-", dir=database_path.parent) as directory:
        temporary = Path(directory) / "demo.duckdb"
        with duckdb.connect(str(temporary)) as connection:
            seed_synthetic_raw(connection, accounts)
            execute_sql_layers(connection)
            connection.execute(
                "CREATE TABLE analytics.dataset_metadata AS "
                "SELECT 'synthetic' AS dataset_kind, 'Deterministic synthetic demo' AS label"
            )
            checks = check_connection(connection, synthetic=True)
            failed = [name for name, check in checks.items() if check["status"] != "pass"]
            if failed:
                raise ValueError(f"Synthetic warehouse checks failed: {failed}")
        temporary.replace(database_path)
    return {"dataset_kind": "synthetic", "accounts": accounts, "checks_passed": len(checks)}
