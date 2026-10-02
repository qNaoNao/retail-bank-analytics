PYTHON ?= python3
ENV_NAME := retail-bank-analytics

.PHONY: help env env-update check test test-pytest download-data audit-source warehouse analysis dashboard verify rebuild

help:
	@echo "make env           Create the Conda environment"
	@echo "make env-update    Update the Conda environment"
	@echo "make check         Run the dependency-free project health check"
	@echo "make test          Run dependency-free unit tests"
	@echo "make test-pytest   Run the full pytest suite inside the environment"
	@echo "make download-data Download Berka data after acknowledging the license caveat"
	@echo "make audit-source  Audit source rows, headers, keys, missingness, and checksums"
	@echo "make warehouse     Rebuild DuckDB and run all data-quality assertions"
	@echo "make analysis      Regenerate evidence-backed findings"
	@echo "make dashboard     Run the local Streamlit dashboard"
	@echo "make verify        Run lint, tests, and the project health check"
	@echo "make rebuild       Rebuild data, warehouse, reports, and verification"

env:
	conda env create -f environment.yml

env-update:
	conda env update -f environment.yml --prune

check:
	PYTHONPATH=src $(PYTHON) scripts/check_setup.py

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

test-pytest:
	pytest

download-data:
	python scripts/download_data.py --acknowledge-license-caveat

audit-source:
	python scripts/audit_source.py

warehouse:
	python scripts/build_warehouse.py

analysis:
	python scripts/generate_analysis.py

dashboard:
	streamlit run app/Home.py

verify:
	ruff check src scripts tests app
	pytest
	python scripts/check_setup.py

rebuild: audit-source warehouse analysis verify
