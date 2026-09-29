# Retail Bank Customer 360

**Growth, Engagement & Credit Risk Analytics with SQL, DuckDB, Python, and Streamlit**

This portfolio project turns eight relational tables from the PKDD'99 Czech Financial Dataset (Berka dataset) into a reproducible retail-bank analytical layer and decision dashboard. The emphasis is on trustworthy metrics, SQL, data modelling, and business interpretation—not on wrapping an AI demo around a dataset.

> Status: project foundation complete; data ingestion is the next milestone. No analytical findings are claimed yet.

## Business questions

1. Which customer and account groups show high value, stable balances, and sustained activity?
2. How does account activity evolve by opening cohort, and where does engagement weaken?
3. Which segments have low card or loan penetration and may merit further product analysis?
4. Where is loan risk concentrated by customer, account, and district characteristics?
5. Which recommended actions are supported by descriptive evidence, and which require an experiment or model?

## Planned deliverables

- Rebuildable ingestion and quality-check pipeline for eight source tables
- DuckDB raw, staging, dimensional, and analytical layers
- Tested SQL metric definitions and business-facing metric dictionary
- Customer 360, value/behaviour segments, activity cohorts, product engagement, and loan-risk analysis
- Filterable Streamlit/Plotly dashboard with drill-down and decision notes
- Recruiter-friendly README, screenshots, architecture, demo script, and interview story

## Quick start

```bash
conda env create -f environment.yml
conda activate retail-bank-analytics
make check
make test-pytest
```

The source data is intentionally excluded from Git. Before downloading it, read [Dataset evaluation](docs/DATASET_EVALUATION.md) and [Data use notice](docs/DATA_USE_NOTICE.md). Then run:

```bash
make download-data
```

## Repository map

```text
app/                 Streamlit application
config/              Non-secret project configuration
data/                 Local-only external/interim/processed data
docs/                 Product spec, metrics, decisions, and portfolio story
notebooks/            Focused exploration only; production logic lives in src/sql
scripts/              Rebuild and validation entry points
sql/                  Staging, marts, analysis, and SQL quality assertions
src/                  Reusable Python package
tests/                Unit, data-contract, and metric tests
```

## Important interpretation limits

- “Retention” means **continued account activity**, not confirmed customer retention; there is no closure or churn label.
- Cross-sell views identify groups for investigation, not causal uplift or sales eligibility.
- Loan status is an outcome. Any optional risk model must use only information available at loan origination.
- The data is historical (1990s Czech banking) and is useful for analytical-method demonstration, not present-day market sizing.

See [PROJECT_SPEC.md](PROJECT_SPEC.md), [ROADMAP.md](ROADMAP.md), and [STATUS.md](STATUS.md) for the agreed scope and progress.
