# Project Status

Last updated: 2026-10-03 (Australia/Sydney)

## Completed milestones

### Milestone 1 — Foundation

Completed:

- Project topic and business scope fixed
- Three candidate datasets compared; Berka selected with license caveat
- Git repository and standard directory structure initialized
- Conda environment and Python package metadata defined
- Data-safety rules and source download gate added
- Dependency-free health check and unit tests added
- Nine-day roadmap, metric starter, JD mapping, and decision log created

Verification:

- Project health check: passed
- Standard-library unit tests: 5 passed
- Python syntax compilation: passed with cache redirected to `work/`
- TOML/YAML parsing: passed
- Git ignore checks for raw data, databases, secrets, outputs, and work files: passed

### Milestone 2 — Data acquisition and source audit

- Created the dedicated `retail-bank-analytics` Conda environment with Python 3.11.
- Confirmed the original university host is no longer resolvable.
- Acquired all eight tables from a public mirror pinned to commit `77e9972...`.
- Recorded SHA-256 checksums for every source table.
- Audited 1,079,680 rows: headers, expected row counts, primary-key uniqueness, and checksums all passed.
- Kept all raw files and generated audit JSON outside Git.
- Added CTU Relational as the current academic repository reference.

## Current milestone

**Milestone 3 — DuckDB staging and quality controls**

1. Load raw tables into DuckDB with source values preserved.
2. Cast keys, amounts, dates, and timestamps in a staging layer.
3. Translate Czech categorical codes without losing raw values.
4. Validate foreign keys, accepted values, date ranges, and row-count reconciliation.
5. Build the first dimensional and monthly-account marts.

## Known risks

- No explicit modern license was found for Berka; raw redistribution remains prohibited by project policy.
- Original university hosting no longer resolves; reproducibility uses a pinned mirror plus checksums.
- Historical codes require translation, but original values must be preserved for traceability.
- Customer-level money metrics can double count joint-access accounts unless owner-only rules are enforced.
