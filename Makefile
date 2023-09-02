# Makefile uses `/bin/bash` shell by default

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
	ruff check .

.PHONY: format
# Automatic fix linting erros for all Python files
format:
	ruff check --fix .

.PHONY: test
# Run all project test suites
test:
	pytest test/

.PHONY: ci
# Run all continuous integration checks
ci: lint test

.PHONY: serve
# Launch a Streamlit dashboard server
serve:
	streamlit run Introduction.py

.PHONY: clean
# Remove all processing artifacts, build files and cache files
clean: clean-data
	rm -f poetry.lock
	rm -rf .ruff_cache/ .pytest_cache/
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '.data' -exec rm -rf {} +

.PHONY: clean-data
# Remove previously collected dataframe
clean-data:
	rm -f data/dataframe.csv

.PHONY: pipeline
# Run data processing pipeline for webcrawler output
pipeline:
	python pipeline/run.py

.PHONY: collect
# Collect data from both web and standalone crawlers
# Before running set `CHROME_DRIVER` environment variable for standalone webcrawls
collect:
	cd crawlers/scrapy; for platform in futurelearn skillshare udemy; do \
		scrapy crawl "$platform" -o ".data/$platform.json" \
	done

	if [[ ! -d "data/.data" ]]; then \
		mkdir -p "data/.data"
	fi

	mv "crawlers/scrapy/.data/*" "data/.data/*" 
	rm -rf "crawlers/scrapy/.data"

	for platform in alison coursera edx pluralsight skillshare; do \
		python -m "crawlers.standalone.$platform" \
	done

	mv "crawlers/standalone/.data/*" "data/.data/*" 
	rm -rf "crawlers/standalone/.data"

