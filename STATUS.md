# Project Status

Last updated: 2026-10-19 (Asia/Shanghai)

## Version 0.2 — Growth analysis and reproducible review

- Reviewed the Jaffle Shop model/test pattern, an independently runnable customer-analytics dashboard architecture, and lifecycle / observation-window practices in a game analytics portfolio. Exact references and adaptations: `docs/REFERENCE_REVIEW.md`.
- Added a complete-month account spine and a reconciled new / retained / reactivated / newly inactive growth bridge.
- Added a day-180 card-free landmark, strictly prior feature windows and mature-only day-[180,360) issuance outcomes.
- Added Wilson intervals, opening-year composition standardization, fixed-horizon sample-size / duration planning, a prospective experiment protocol and an offline HTML report.
- Added a deterministic synthetic eight-table demo using the same transformation pipeline. No source data is downloaded for demo or CI.
- Fixed empty-selection risk filtering, stale query caching and nondeterministic quartile ties. Historical rebuilds validate before replacing the prior database.
- Historical warehouse: 28 quality assertions pass. Local Python 3.11 full suite: 34 tests pass. Source-only checks run the synthetic pipeline / app and explicitly skip historical-only checks.
- Configured CI for Python 3.11/3.12 with maintained Node 24 actions and an explicit Ubuntu 24.04 runner. Remote CI has not run for these changes because nothing was pushed this round.
- Refreshed README, metrics, model grains, interview/demo materials and a Chinese GitHub Desktop upload guide.

The code upgrade is local and uncommitted. No GitHub upload, public deployment or historical rewrite was performed in this round. The earlier browser-note cleanup commit may still be ahead of origin.

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

### Milestone 4 — Business analysis and dashboard

- Generated evidence-backed portfolio, customer, product, cohort, funnel, and lending-risk findings.
- Built a five-tab Streamlit/Plotly dashboard with global filters and account drill-down.
- Reconciled displayed KPIs to governed SQL definitions and warehouse tests.
- Added a Streamlit render smoke test and visually checked all dashboard tabs.
- Confirmed the browser console has no application errors.
- Documented the model no-go decision: 31 finished-loan defaults are insufficient for a defensible promoted model.

### Milestone 5 — Portfolio packaging

- Replaced the starter README with the portfolio pitch, verified results, architecture, rebuild guide, and responsible-use notes.
- Added a three-minute demo script, interview guide, résumé bullets, deployment decision, and CI workflow.
- Preserved milestone commits instead of rewriting the learning history.
- Completed a clean end-to-end rebuild from local source: 1,079,680 rows audited, 20 data-quality assertions passed, Ruff passed, 11 pytest tests passed, and the repository health check passed.

## Current state

**Version 0.2 is ready for a local analytics portfolio demo.**

The historical dashboard remains local because raw and transformed row-level data are excluded from Git. A code-only GitHub repository already exists; this round's upgrades have not been uploaded. A new reviewer can run the independent synthetic demo without obtaining the historical source.

## Known risks

- No explicit modern license was found for Berka; raw redistribution remains prohibited by project policy.
- Original university hosting no longer resolves; reproducibility uses a pinned mirror plus checksums.
- Historical codes require translation, but original values must be preserved for traceability.
- Customer-level money metrics can double count joint-access accounts unless owner-only rules are enforced.
