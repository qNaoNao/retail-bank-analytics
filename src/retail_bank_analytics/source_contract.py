"""Expected source-table contracts for the PKDD'99 financial dataset."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceTableContract:
    filename: str
    columns: tuple[str, ...]
    primary_key: str
    expected_rows: int


SOURCE_CONTRACTS = {
    "account": SourceTableContract(
        "account.asc", ("account_id", "district_id", "frequency", "date"), "account_id", 4500
    ),
    "card": SourceTableContract(
        "card.asc", ("card_id", "disp_id", "type", "issued"), "card_id", 892
    ),
    "client": SourceTableContract(
        "client.asc", ("client_id", "birth_number", "district_id"), "client_id", 5369
    ),
    "disp": SourceTableContract(
        "disp.asc", ("disp_id", "client_id", "account_id", "type"), "disp_id", 5369
    ),
    "district": SourceTableContract(
        "district.asc", tuple(f"A{i}" for i in range(1, 17)), "A1", 77
    ),
    "loan": SourceTableContract(
        "loan.asc",
        ("loan_id", "account_id", "date", "amount", "duration", "payments", "status"),
        "loan_id",
        682,
    ),
    "order": SourceTableContract(
        "order.asc",
        ("order_id", "account_id", "bank_to", "account_to", "amount", "k_symbol"),
        "order_id",
        6471,
    ),
    "trans": SourceTableContract(
        "trans.asc",
        (
            "trans_id",
            "account_id",
            "date",
            "type",
            "operation",
            "amount",
            "balance",
            "k_symbol",
            "bank",
            "account",
        ),
        "trans_id",
        1_056_320,
    ),
}
