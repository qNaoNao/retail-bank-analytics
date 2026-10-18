# Synthetic Test Fixtures

Files placed here must be tiny, newly created synthetic records used only for automated tests. Do not copy rows from the Berka source dataset into this directory.

The independent eight-table fixture implementation is `src/retail_bank_analytics/demo.py`; generated records and database files are not committed. `tests/test_growth.py` separately constructs hand-calculated edge cases in memory. The full fixture uses more accounts for a local demo and 32 accounts for CI.
