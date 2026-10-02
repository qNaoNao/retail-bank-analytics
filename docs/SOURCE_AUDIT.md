# Source Data Audit

Generated: 2026-10-02T21:36:09.923574+00:00

Overall status: **PASS**

Total source rows: **1,079,680**

| Table | Rows | Expected | PK duplicates | Missing cells | Checksum | Status |
|---|---:|---:|---:|---:|---|---|
| account | 4,500 | 4,500 | 0 | 0 | match | pass |
| card | 892 | 892 | 0 | 0 | match | pass |
| client | 5,369 | 5,369 | 0 | 0 | match | pass |
| disp | 5,369 | 5,369 | 0 | 0 | match | pass |
| district | 77 | 77 | 0 | 2 | match | pass |
| loan | 682 | 682 | 0 | 0 | match | pass |
| order | 6,471 | 6,471 | 0 | 1,379 | match | pass |
| trans | 1,056,320 | 1,056,320 | 0 | 2,262,171 | match | pass |

## Interpretation

- Row counts, headers, primary-key uniqueness, and pinned-file checksums match the contract.
- Missing cells are expected in optional transaction counterparty fields and selected district rates.
- Fourteen zero-amount rows are retained because they are rounded interest or penalty-interest records; negative amounts are not present.
- This audit validates source integrity only; foreign keys, accepted codes, dates, and business rules are tested in the DuckDB staging pipeline.
- Raw source files remain excluded from Git.
