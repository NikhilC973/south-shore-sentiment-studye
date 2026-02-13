# ============================================================
# Aftermath_Sentiment_Study — Makefile
# ============================================================
.PHONY: help install hooks-install init-db ingest ingest-synthetic clean-data analyze dashboard report run-all test lint

PYTHON = python
STREAMLIT = streamlit

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and package in editable mode
	pip install -r requirements.txt
	pip install -e .  # Install package in editable mode so src imports work
	$(PYTHON) -m spacy download en_core_web_sm
	@echo "✅ Dependencies installed and package configured"

hooks-install: ## Install git pre-commit hooks (run once per clone)
	$(PYTHON) -m pre_commit install
	@echo "✅ pre-commit hooks installed"


init-db: ## Initialize DuckDB database
	$(PYTHON) -c "from src.utils.db import init_database; init_database()"
	@echo "✅ Database initialized"

ingest: ## Collect data from Reddit + News sources
	$(PYTHON) -m src.ingestion.pipeline --mode live
	@echo "✅ Data ingestion complete"

ingest-synthetic: ## Generate synthetic fallback data
	$(PYTHON) -m src.ingestion.pipeline --mode synthetic
	@echo "✅ Synthetic data generated"

clean-data: ## Run text cleaning pipeline
	$(PYTHON) -m src.analysis.cleaning
	@echo "✅ Data cleaning complete"

analyze: ## Run full analysis (sentiment + emotion + topics + geo)
	$(PYTHON) -m src.analysis.sentiment
	$(PYTHON) -m src.analysis.emotions
	$(PYTHON) -m src.analysis.topics
	$(PYTHON) -m src.analysis.geo_tagger
	$(PYTHON) -m src.analysis.phase_tagger
	$(PYTHON) -m src.analysis.longitudinal
	@echo "✅ Analysis complete"

dashboard: ## Launch Streamlit dashboard
	$(STREAMLIT) run dashboards/app.py --server.port 8501

report: ## Generate PDF report
	$(PYTHON) -m src.visualization.report_generator
	@echo "✅ Report generated"

run-all: init-db ingest-synthetic clean-data analyze report ## Run full pipeline end-to-end
	@echo "🎉 Full pipeline complete"

test: ## Run test suite
	$(PYTHON) -m pytest tests/ -v --cov=src

lint: ## Code quality checks
	ruff check src/ tests/ dashboards/
	ruff format --check src/ tests/ dashboards/

format: ## Auto-format code and fix linting issues
	ruff format src/ tests/ dashboards/
	ruff check --fix src/ tests/ dashboards/

pre-commit-fix: format ## Run formatting/linting before committing (use this before git commit)
	@echo "✅ Code formatted and linted. You can now commit."
