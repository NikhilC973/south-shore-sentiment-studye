# Methodology — South Shore Sentiment Study

## Overview
This document details the complete analytical methodology used to measure community sentiment evolution around the September 30, 2025 ICE/CBP enforcement action in South Shore, Chicago.

## Data Collection Strategy

### Reddit (No Official API)
After two rejections from Reddit's official API program (both developer and researcher accounts), we employ three fully legal public-access alternatives:

1. **PullPush.io** (Primary) — Successor to the Pushshift archive. Provides historical search across all public Reddit submissions and comments. Rate-limited to 1 request per 2 seconds.

2. **Old Reddit JSON** (Fallback) — Any Reddit URL can be accessed as JSON by appending `.json`. Provides current/recent data. Rate-limited to 1 request per 2.5 seconds with respectful User-Agent.

3. **Arctic Shift** (Bulk Backfill) — Monthly data dumps of all public Reddit data for large-scale historical analysis.

### News Comment Sections
BeautifulSoup-based scraping of publicly accessible comment sections, respecting robots.txt directives and rate limits (minimum 3 seconds between requests).

## NLP Pipeline

### Stage 1: Text Cleaning
- URL and username stripping
- Hashtag conversion (#Tag → Tag)
- Reddit markers ([deleted], [removed]) removal
- Whitespace normalization
- Deduplication via MD5 text hashing
- Quality flagging (short < 3 words, spam detection, non-English detection)

### Stage 2: Sentiment Scoring
- **VADER**: Lexicon-based polarity (compound, positive, negative, neutral)
- **RoBERTa**: `cardiffnlp/twitter-roberta-base-sentiment-latest` — fine-tuned on social media for positive/negative/neutral classification

### Stage 3: Emotion Analysis
- **GoEmotions**: `monologg/bert-base-cased-goemotions-original` — 27 emotion labels mapped to 8 targets
- Confidence threshold: 0.3 minimum probability
- Dominant emotion: highest probability above threshold

### Stage 4: Topic Discovery
- **BERTopic** with `all-MiniLM-L6-v2` sentence embeddings
- HDBSCAN clustering with minimum topic size of 5
- Fallback: keyword-based topic assignment when BERTopic unavailable

### Stage 5: Longitudinal Analysis
- Phase assignment based on temporal windows
- Bootstrapped 95% confidence intervals (1000 iterations)
- Daily emotion curves with smoothing
- Platform contrast analysis (Reddit vs. News)
- Trajectory detection (rising, declining, peak patterns)

## Quality Control
- Stratified sample of 100 posts manually reviewed across phases and platforms
- Confusion points documented and thresholds recalibrated as needed
- Deduplication removes exact and near-duplicate posts
