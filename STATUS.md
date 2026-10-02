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

### Milestone 3 — DuckDB staging and quality controls

- Built 38 raw, staging, mart, and analytics tables/views from version-controlled SQL.
- Preserved original codes while adding typed dates, amounts, directions, and English labels.
- Added dimensions, facts, the account-client bridge, account-month, customer 360, cohort, onboarding, and loan-risk marts.
- Enforced owner-only money attribution to prevent authorized-user double counting.
- Added origination-time loan features whose transaction window ends before the loan date.
- Passed 20 executable zero-row quality assertions and five warehouse integration tests.
- Investigated and documented 14 valid zero-amount interest/penalty-interest records.

## Current milestone

**Milestone 4 — Business analysis and dashboard**

1. Generate evidence-backed portfolio, segment, cohort, funnel, and risk findings.
2. Build the filterable Streamlit/Plotly dashboard and account drill-down.
3. Add screenshots and a local demo runbook.
4. Reconcile every displayed KPI to the metric dictionary and SQL tests.

## Known risks

- No explicit modern license was found for Berka; raw redistribution remains prohibited by project policy.
- Original university hosting no longer resolves; reproducibility uses a pinned mirror plus checksums.
- Historical codes require translation, but original values must be preserved for traceability.
- Customer-level money metrics can double count joint-access accounts unless owner-only rules are enforced.
