PYTHON ?= python3
ENV_NAME := retail-bank-analytics

.PHONY: help env env-update check test test-pytest download-data

help:
	@echo "make env           Create the Conda environment"
	@echo "make env-update    Update the Conda environment"
	@echo "make check         Run the dependency-free project health check"
	@echo "make test          Run dependency-free unit tests"
	@echo "make test-pytest   Run the full pytest suite inside the environment"
	@echo "make download-data Download Berka data after acknowledging the license caveat"

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
