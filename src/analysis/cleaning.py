"""
Text Cleaning Pipeline — Normalization, deduplication, and phase tagging.

Updated: Extended phase detection to 7 phases (through Dec 12, 2025).
"""

import hashlib
import re
from datetime import datetime

import duckdb
import pandas as pd

from src.utils.constants import (
    PHASES,
    TABLE_POSTS_CLEAN,
    TABLE_POSTS_RAW,
)
from src.utils.db import get_connection
from src.utils.logger import log

# ── Text Cleaning ────────────────────────────────────────────


def clean_text(text: str) -> str:
    """Normalize a post's text for NLP processing."""
    if not isinstance(text, str):
        return ""

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove Reddit-specific markdown
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # [text](url) → text
    text = re.sub(r"/?r/\w+", "", text)  # r/subreddit
    text = re.sub(r"/?u/\w+", "", text)  # u/username
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove very short results
    if len(text) < 10:
        return ""

    return text


def detect_phase(dt_str: str) -> str:
    """Assign temporal phase based on datetime string.

    Supports 7 phases:
      pre, event, post_week1, post_week2, post_weeks3_5,
      court_action, displacement
    """
    try:
        if isinstance(dt_str, datetime):
            dt = dt_str
        else:
            dt = pd.to_datetime(dt_str, utc=True)

        date_str = dt.strftime("%Y-%m-%d")

        for phase_name, phase_info in PHASES.items():
            if phase_info["start"] <= date_str <= phase_info["end"]:
                return phase_name

        return "outside_window"
    except Exception:
        return "unknown"


def compute_text_hash(text: str) -> str:
    """SHA-256 hash for deduplication."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ── Main Pipeline ────────────────────────────────────────────


def run_cleaning():
    """Execute the full cleaning pipeline."""
    con = get_connection()

    # Load raw posts
    try:
        df = con.execute(f"SELECT * FROM {TABLE_POSTS_RAW}").fetchdf()
    except duckdb.CatalogException:
        log.error(f"Table {TABLE_POSTS_RAW} does not exist. Run ingestion first.")
        return

    log.info(f"Loaded {len(df)} raw posts")

    # Clean text
    df["text_clean"] = df["text"].apply(clean_text)
    df = df[df["text_clean"].str.len() > 0].copy()
    log.info(f"After text cleaning: {len(df)} posts")

    # Deduplicate by text hash
    df["text_hash"] = df["text_clean"].apply(compute_text_hash)
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["text_hash"], keep="first").copy()
    log.info(f"Deduplication: {before_dedup} → {len(df)} ({before_dedup - len(df)} removed)")

    # Phase tagging
    df["phase"] = df["dt_utc"].astype(str).apply(detect_phase)

    # Filter out posts outside analysis window
    valid_phases = list(PHASES.keys())
    df = df[df["phase"].isin(valid_phases)].copy()
    log.info(f"After date filtering: {len(df)} posts within analysis window")

    # Log phase distribution
    phase_dist = df["phase"].value_counts().to_dict()
    log.info(f"Phase distribution: {phase_dist}")

    # Word count
    df["word_count"] = df["text_clean"].str.split().str.len()

    # Store to DuckDB
    con.execute(f"DROP TABLE IF EXISTS {TABLE_POSTS_CLEAN}")
    con.execute(f"""
        CREATE TABLE {TABLE_POSTS_CLEAN} AS
        SELECT
            id, platform, source, url, dt_utc,
            text AS text_original,
            text_clean,
            text_hash,
            title,
            author_display,
            score,
            like_count,
            reply_count,
            share_count,
            parent_id,
            post_type,
            phase,
            word_count
        FROM df
    """)

    count = con.execute(f"SELECT COUNT(*) FROM {TABLE_POSTS_CLEAN}").fetchone()[0]
    log.info(f"Stored {count} clean posts to {TABLE_POSTS_CLEAN}")
    con.close()


if __name__ == "__main__":
    run_cleaning()
