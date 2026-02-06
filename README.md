# 🏘️ South Shore Sentiment Study — ICE Raid Aftermath Analysis (2025)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io)
[![DuckDB](https://img.shields.io/badge/DuckDB-Analytical_Engine-FEF000.svg)](https://duckdb.org)

> **Measuring how public sentiment in South Shore and adjacent Chicago neighborhoods evolved before and after the September 30, 2025 ICE/CBP raid — mapping emotional trajectories from fear → anger → solidarity → resilience.**

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Folder Structure](#-folder-structure)
- [Setup & Installation](#-setup--installation)
- [Pipeline Execution](#-pipeline-execution)
- [Data Sources](#-data-sources)
- [Methodology](#-methodology)
- [Dashboard](#-dashboard)
- [Ethics & Governance](#-ethics--governance)
- [Results](#-results)
- [Contributing](#-contributing)

---

## 🎯 Project Overview

**Anchor Event:** ICE/CBP enforcement action in South Shore, Chicago — September 30, 2025 (t=0)

**Analysis Window:** Sep 16 – Oct 14, 2025 (±14 days), extended to Nov 7 for sustained effects

**Objective:** Produce actionable timing guidance for community outreach and services by tracking emotional arcs across:
- Reddit communities (r/Chicago, r/news, r/Illinois, r/politics, etc.)
- News comment sections (Block Club, WBEZ, Sun-Times, South Side Weekly)

### Key Deliverables
| Deliverable | Description |
|-------------|-------------|
| **Sentiment Pipeline** | End-to-end NLP pipeline: ingestion → cleaning → emotion tagging → topic modeling |
| **Longitudinal Analysis** | Emotion-over-time curves with bootstrapped CIs across phases |
| **Interactive Dashboard** | Streamlit app with Overview, Themes, Geography, Methodology tabs |
| **Program Guidance** | Timing recommendations for crisis comms, legal aid, mutual aid |
| **Public Report** | 10-12 page PDF with executive summary and limitations |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
│  Reddit (PRAW-free)  │  News Comments (BS4)  │  Synthetic  │
└──────────┬───────────┴──────────┬────────────┴──────┬──────┘
           │                      │                    │
           ▼                      ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   INGESTION LAYER                           │
│  PullPush.io API  │  BeautifulSoup  │  Synthetic Generator  │
│  Old Reddit JSON  │  Newspaper3k    │  Faker + Templates    │
└──────────┬───────────────────────┬───────────────────┬──────┘
           │                       │                    │
           ▼                       ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE (DuckDB)                          │
│  posts_raw  │  posts_clean  │  posts_emotions  │  topics    │
└──────────┬──────────────────┬────────────────────────┬──────┘
           │                  │                         │
           ▼                  ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ANALYSIS ENGINE                            │
│  VADER + RoBERTa  │  GoEmotions  │  BERTopic  │  spaCy NER │
└──────────┬──────────────────┬────────────────────────┬──────┘
           │                  │                         │
           ▼                  ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│               VISUALIZATION & OUTPUT                        │
│  Plotly Curves  │  Streamlit Dashboard  │  PDF Report       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
south-shore-sentiment-study/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI
├── config/
│   ├── settings.yaml                 # Central config (queries, thresholds, paths)
│   ├── source_registry.yaml          # Data source compliance registry
│   └── .env.example                  # Environment template
├── data/
│   ├── raw/                          # Immutable ingested data
│   ├── processed/                    # Cleaned + enriched parquets
│   ├── synthetic/                    # Generated synthetic fallback data
│   └── exports/                      # Aggregated outputs for sharing
├── docs/
│   ├── ETHICS.md                     # Ethical use statement
│   ├── METHODOLOGY.md                # Full methodology writeup
│   ├── LIMITATIONS.md                # Known limitations
│   └── report/                       # Final PDF report assets
├── src/
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── reddit_collector.py       # PullPush.io + Old Reddit JSON
│   │   ├── news_collector.py         # News comment scraping
│   │   ├── synthetic_generator.py    # Realistic synthetic data
│   │   └── pipeline.py              # Orchestrator for all sources
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── cleaning.py               # Text normalization + dedup
│   │   ├── sentiment.py              # VADER + RoBERTa scoring
│   │   ├── emotions.py               # GoEmotions multi-label
│   │   ├── topics.py                 # BERTopic modeling
│   │   ├── geo_tagger.py             # Neighborhood mention extraction
│   │   ├── phase_tagger.py           # Temporal phase assignment
│   │   └── longitudinal.py           # Time-series analysis + CIs
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── emotion_curves.py         # Plotly emotion trajectories
│   │   ├── topic_charts.py           # BERTopic visualizations
│   │   ├── geo_charts.py             # Neighborhood comparisons
│   │   └── report_generator.py       # PDF report builder
│   └── utils/
│       ├── __init__.py
│       ├── db.py                      # DuckDB connection manager
│       ├── logger.py                  # Structured logging
│       └── constants.py               # Shared constants
├── dashboards/
│   └── app.py                        # Streamlit dashboard
├── tests/
│   ├── test_cleaning.py
│   ├── test_sentiment.py
│   └── test_pipeline.py
├── notebooks/
│   └── 01_eda_exploration.ipynb
├── Makefile                          # Task runner
├── pyproject.toml                    # Modern Python packaging
├── requirements.txt                  # Pinned dependencies
├── LICENSE
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- 8GB+ RAM (for transformer models)

### Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/south-shore-sentiment-study.git
cd south-shore-sentiment-study

# Environment
cp config/.env.example .env
python -m venv .venv && source .venv/bin/activate

# Install
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Initialize database
make init-db

# Run full pipeline
make run-all
```

### Make Commands

```bash
make ingest          # Collect data from all sources
make ingest-synthetic # Generate synthetic fallback data
make clean-data      # Run text cleaning pipeline
make analyze         # Run sentiment + emotion + topic analysis
make dashboard       # Launch Streamlit dashboard
make report          # Generate PDF report
make run-all         # Execute full pipeline end-to-end
make test            # Run test suite
make lint            # Code quality checks
```

---

## 📊 Data Sources

### Reddit (No Official API Required)
Since Reddit's official API access was denied, we use **fully legal public-access alternatives**:

| Method | Endpoint | Rate Limit | Notes |
|--------|----------|------------|-------|
| **PullPush.io** | `api.pullpush.io/reddit/search` | Respectful pacing | Pushshift successor; public Reddit archive |
| **Old Reddit JSON** | `old.reddit.com/r/{sub}/.json` | 1 req/2s | Append `.json` to any Reddit URL |
| **Arctic Shift** | `arctic-shift.io` | Bulk dumps | Monthly Reddit data dumps |

### Target Subreddits
`r/Chicago`, `r/news`, `r/Illinois`, `r/AskChicago`, `r/50501Chicago`, `r/EyesOnIce`, `r/moderatepolitics`, `r/politics`, `r/ICE_Raids`, `r/WindyCity`, `r/AskConservatives`, `r/somethingiswrong2024`

### News Sources (Comment Scraping)
Block Club Chicago, WBEZ, Chicago Sun-Times, South Side Weekly, AP News

---

## 🔬 Methodology

### Phase Definitions
| Phase | Window | Description |
|-------|--------|-------------|
| `pre` | Sep 16–29 | Baseline sentiment before raid |
| `event` | Sep 30 ± 24h | Immediate reaction window |
| `post_week1` | Oct 1–7 | Early aftermath |
| `post_week2` | Oct 8–14 | Stabilization period |
| `post_weeks3_5` | Oct 15–Nov 7 | Extended monitoring |

### NLP Stack
- **VADER**: Polarity baseline (positive/negative/neutral/compound)
- **RoBERTa** (`cardiffnlp/twitter-roberta-base-sentiment-latest`): Fine-tuned social media sentiment
- **GoEmotions** (`monologg/bert-base-cased-goemotions-original`): 27-label emotion taxonomy → mapped to 8 target emotions
- **BERTopic**: Dynamic topic modeling with temporal tracking
- **spaCy**: NER and geo-mention extraction

---

## 📈 Dashboard

The Streamlit dashboard includes:

1. **Overview** — Emotion trajectory curves with confidence intervals
2. **Themes** — BERTopic clusters with top terms and exemplar posts
3. **Geography** — Neighborhood-level sentiment heatmaps
4. **Methodology** — Ethics statement, verification levels, limitations
5. **Program Guidance** — Actionable recommendations with timing

---

## ⚖️ Ethics & Governance

- **Public data only** — No private messages, no login-required content
- **No PII** — Usernames stripped; no doxxing; no precise addresses
- **Aggregate outputs only** — Individual posts never published verbatim
- **Verification levels** — Official (FOIA/press), Two-source (media), Single-source (social)
- **Removal channel** — Organizations can request data removal

See [docs/ETHICS.md](docs/ETHICS.md) for the full Ethical Use Statement.

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

**Built with ❤️ for Chicago's South Shore community**
