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

.PHONY: pylint
# Verify proper formatting for Python files
pylint:
	ruff check .

.PHONY: pyformat
# Automatic fix linting erros for all Python files
pyformat:
	ruff check --fix .

.PHONY: serve
# Launch a Streamlit dashboard server
serve:
	streamlit run Introduction.py

