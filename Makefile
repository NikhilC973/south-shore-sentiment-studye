# ============================================================
# South Shore Sentiment Study — Makefile
# ============================================================
.PHONY: help install init-db ingest ingest-synthetic clean-data analyze dashboard report run-all test lint

PYTHON = python
STREAMLIT = streamlit

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	$(PYTHON) -m spacy download en_core_web_sm
	@echo "✅ Dependencies installed"

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

format: ## Auto-format code
	ruff format src/ tests/ dashboards/
