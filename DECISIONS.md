# Decision Log

## ADR-001 — Use Berka / PKDD'99 as the primary dataset

**Decision:** Use the real, anonymized Czech bank dataset as the project core because its eight related tables and transaction history support customer 360, SQL depth, cohort activity, product engagement, and lending risk in one coherent story.

**Trade-off:** The original challenge was publicly distributed, but no explicit modern data license was found on the archived description. We will not commit or redistribute the raw files. The public repository will contain source links, acquisition code, attribution, and a clear caveat. If a hosting platform requires an explicit reusable-data license, use the documented UCI fallback rather than silently republishing Berka.

**2026-10-03 implementation note:** The original `sorry.vse.cz` host no longer resolves. The current academic reference is CTU Relational, which exposes the same eight-table dataset through a public read-only database. For deterministic file acquisition, the pipeline uses the public `jlacko/berka-dataset` mirror pinned to commit `77e9972...` and verifies every file with SHA-256. This changes distribution mechanics, not the license caveat.

## ADR-002 — Use DuckDB instead of a server database

**Decision:** Use DuckDB for a local analytical warehouse. It supports substantial SQL, window functions, Parquet, fast local execution, and a zero-server setup that works on macOS and is easy for recruiters to reproduce.

**Trade-off:** This does not demonstrate database administration. The project instead prioritizes analytical SQL and modelling, which are more relevant to the target roles and delivery window.

## ADR-003 — Define retention as account activity retention

**Decision:** A cohort is retained in month N when the account has a qualifying transaction in that relative month.

**Reason:** The source has account-open dates and transactions but no reliable closure or churn label. Dashboard and documentation must say “activity retention,” never imply confirmed customer retention.

## ADR-004 — Keep raw and generated data out of Git

**Decision:** Raw archives, extracted data, DuckDB files, generated models, logs, and local outputs are ignored. Small test fixtures must be clearly marked synthetic and live only under `tests/fixtures/`.

## ADR-005 — Make modelling optional and leakage-gated

**Decision:** Complete the analytical product before adding a model. A baseline model is included only if an as-of date and origination-time feature set can be defended. Loan status, post-origination transactions, and future balances cannot be predictors.

**2026-10-03 outcome:** Do not promote a predictive model in v1. Only 234 loans have finished outcomes and 31 defaulted. The project delivers the leakage-safe feature mart, a documented model gate, and descriptive risk analysis instead of an unstable headline score.

## ADR-006 — Keep the supported dashboard demo local

**Decision:** Ship the Streamlit application as a reproducible local demo and do not publish the row-level DuckDB database.

**Reason:** The source is public research data, but no explicit modern redistribution licence was found. A public deployment can be reconsidered only with permission, a licensed replacement dataset, or approved aggregate extracts.

## ADR-007 — Use independent synthetic sources for review and CI

**Decision (2026-10-19):** Generate a small, deterministic eight-table source without copying historical rows. Run the same SQL layers and portable assertions, label the application mode, and reject synthetic input in the historical memo generator. Historical row-count/checksum contracts remain separate and mandatory for a historical rebuild.

**Reason:** A reviewer should be able to execute meaningful checks from a source-only clone. Generated data and database files remain untracked; generation code and tests are included.

## ADR-008 — Decompose growth and use a day-180 adoption landmark

**Decision:** Report new, retained, reactivated and newly inactive account-months on a complete-month spine. For prospective card analysis, use features in [opening, day 180) and an issuance outcome in [day 180, day 360), with full follow-up and no card before the landmark. Missing future labels are NULL.

**Reason:** All historical accounts meet the existing 30-day activation definition. The earliest historical card issuance occurs on day 203. A 30/90-day issuance endpoint or a churn model would not match this source. Raw group comparisons and common-opening-year standardized rates remain observational.

## ADR-009 — Validate before replacing a warehouse

**Decision:** Build historical and demo warehouses in unique staging directories, validate, close the connection and atomically replace the published file. Preserve the previous warehouse on build failure. Include database path and file modification version in dashboard cache keys; use account ID to break ties in segment quartiles.

**Reason:** A failed refresh should not remove the last usable demo, and rebuilds should not silently return stale metrics or unstable tied segment assignments.
