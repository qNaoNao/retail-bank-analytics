# Deployment Plan

## Supported demo: local Streamlit

The primary supported demo runs on macOS or Linux with the documented Conda environment:

```bash
conda activate retail-bank-analytics
make warehouse
make analysis
make dashboard
```

The application reads a local, Git-ignored DuckDB file in read-only mode. This is the safest reproducible setup while the source dataset lacks an explicit modern redistribution licence.

## Public hosting decision

The code is ready for Streamlit Community Cloud, but the database cannot be committed because it contains transformed row-level source data. Public hosting therefore requires one of these reviewed options:

1. Obtain explicit permission to host the transformed database.
2. Replace Berka with the documented CC BY 4.0 UCI fallback and adapt the narrower dashboard.
3. Host only approved aggregate extracts after confirming that derived-data publication is permitted.
4. Use a recorded walkthrough plus the public code repository, while keeping the live dashboard local.

For the current portfolio, option 4 is recommended. It preserves the stronger multi-table story without pretending that public availability grants redistribution rights.

## Deployment checklist

- Run `make verify` from a clean clone.
- Confirm `.env`, raw files, DuckDB, logs, and outputs are not tracked.
- Verify data-source attribution and licensing caveat remain visible.
- Capture dashboard screenshots or a short walkthrough from the rebuilt local app.
- Confirm every displayed KPI reconciles to a tested SQL definition.
- Do not add API keys; the app needs none.

