# Project Status

Last updated: 2026-09-29 (Australia/Sydney)

## Current milestone

**Milestone 1 — Foundation: complete**

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

## Next milestone

**Milestone 2 — Data acquisition and source audit**

1. Confirm the official archive endpoint and report its actual compressed/expanded size.
2. Download outside Git and record a SHA-256 checksum.
3. Inventory the eight files, row counts, columns, encoding, delimiters, and date/code formats.
4. Produce a machine-readable data contract and human-readable quality report.
5. Decide whether any source anomaly needs a documented correction rule.

## Known risks

- No explicit modern license was found for Berka; raw redistribution remains prohibited by project policy.
- Original university hosting is old and may be intermittently unavailable.
- Historical codes require translation, but original values must be preserved for traceability.
- Customer-level money metrics can double count joint-access accounts unless owner-only rules are enforced.
