# Dashboard

Run `python -m streamlit run app/Home.py` after installing the project. A source-only clone defaults to independently generated synthetic data; the Historical Berka option requires `make warehouse`.

Six tabs consume governed marts: overview, Customer 360, cohort/funnel, growth/experiments, lending risk and definitions. Source selection is explicit; source type and observation date remain visible. Sidebar filters apply only to Customer 360 and Lending risk. The growth tab uses pre-landmark features and its own opening-year filter.

Query-cache keys include the database path and modification version. Automated application tests cover an empty region selection, synthetic labels, growth controls and render errors. `RETAIL_BANK_DATABASE` can point a test process at an isolated fixture database.
