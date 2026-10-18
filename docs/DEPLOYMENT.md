# Deployment Plan

## Source-only demo

Install with `python -m pip install -e ".[dev]"`, then launch `python -m streamlit run app/Home.py`. Without a historical database it builds / selects the independent synthetic demo. `make demo` can prepare it explicitly. Generated demo records and databases stay outside Git; the generator and tests are version-controlled.

This path supports inspection on a new machine without licensing or source-mirror access. Synthetic figures are clearly labelled, and the historical report generator rejects a synthetic warehouse. No public deployment is performed automatically.

## Supported demo: local Streamlit

The primary supported demo runs on macOS or Linux with the documented Conda environment:

```bash
conda activate retail-bank-analytics
make warehouse
make analysis
make dashboard
```

The application reads a local, Git-ignored DuckDB file in read-only mode. This is the safest reproducible setup while the source dataset lacks an explicit modern redistribution licence.

`make growth-report` also generates `outputs/growth_report.html`, a self-contained local report with embedded Plotly code, data and the decision memo. It can be opened without running Streamlit. Historical report outputs remain Git-ignored under the existing data-publication policy.

## Public hosting decision

The code is ready for Streamlit Community Cloud, but the database cannot be committed because it contains transformed row-level source data. Public hosting therefore requires one of these reviewed options:

1. Obtain explicit permission to host the transformed database.
2. Replace Berka with the documented CC BY 4.0 UCI fallback and adapt the narrower dashboard.
3. Host only approved aggregate extracts after confirming that derived-data publication is permitted.
4. Use a recorded walkthrough plus the public code repository, while keeping the live dashboard local.

For historical results, option 4 remains supported. A future public demo can run the independently generated synthetic warehouse instead, with its banner preserved. That deployment would demonstrate software behavior, not reproduce the historical findings.

## Deployment checklist

- Run `make verify` from a clean clone.
- Confirm `.env`, raw files, DuckDB, logs, and outputs are not tracked.
- Verify data-source attribution and licensing caveat remain visible.
- Capture dashboard screenshots or a short walkthrough from the rebuilt local app.
- Confirm every displayed KPI reconciles to a tested SQL definition.
- Do not add API keys; the app needs none.

