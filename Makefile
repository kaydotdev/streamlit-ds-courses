# Makefile uses `/bin/bash` shell by default
# Before running Makefile, activate virtual environment with `poetry shell`

.PHONY: all-dep
# Installing dependencies for development, processing and dashboard
all-dep:
	poetry install --with dev,pipeline

.PHONY: min-dep
# Installing dependencies for dashboard only
min-dep:
	poetry install

.PHONY: lint
# Verify proper formatting for Python files
lint:
	ruff check .

.PHONY: format
# Automatic fix linting erros for all Python files
format:
	ruff check --fix .

.PHONY: test
# Run all project test suites
test:
	pytest test/

.PHONY: serve
# Launch a Streamlit dashboard server
serve:
	streamlit run Introduction.py

.PHONY: clean
# Remove all generates files
clean:
	rm -f data/*

.PHONY: pipeline
# Run data processing pipelines
pipeline:
	rm -f data/dataframe.csv
	python pipeline/run.py
	rm -rf data/intr/

