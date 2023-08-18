# Makefile uses `/bin/bash` shell by default
# Before running Makefile, activate virtual environment with `poetry shell`

.PHONY: all-dep
# Installing dependencies for development, processing and dashboard
all-dep:
	poetry install --with dev,pipeline,webcrawl

.PHONY: min-dep
# Installing dependencies for dashboard only
min-dep:
	poetry install

.PHONY: lint
# Verify proper formatting for Python files
lint:
	poetry run ruff check .

.PHONY: format
# Automatic fix linting erros for all Python files
format:
	poetry run ruff check --fix .

.PHONY: test
# Run all project test suites
test:
	poetry run pytest test/

.PHONY: serve
# Launch a Streamlit dashboard server
serve:
	poetry run streamlit run Introduction.py

.PHONY: clean
# Remove all processing artifacts, build files and cache files
clean: clean-data
	rm -f poetry.lock
	rm -rf .ruff_cache/ .pytest_cache/
	find . -type d -name '__pycache__' -exec rm -rf {} +

.PHONY: clean-data
# Remove previously collected dataframe
clean-data:
	rm -f data/dataframe.csv

.PHONY: pipeline
# Run data processing pipeline for webcrawler output
pipeline:
	poetry run python pipeline/run.py

