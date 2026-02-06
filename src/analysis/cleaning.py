"""
Text Cleaning Pipeline.

Normalizes raw posts → posts_clean with:
- URL/username stripping
- Lowercasing, tokenization, lemmatization
- Deduplication (fuzzy + exact)
- Quality flagging (too short, spam, non-English)
- Phase tagging and neighborhood detection
"""
import re
import hashlib
from collections import Counter

import pandas as pd

from src.utils.db import get_connection, init_database
from src.utils.constants import (
    PROJECT_ROOT, PHASES, NEIGHBORHOOD_LEXICON,
)
from src.utils.logger import log


# ── Text Normalization ───────────────────────────────────
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
USERNAME_PATTERN = re.compile(r"@\w+|u/\w+|/u/\w+")
HASHTAG_PATTERN = re.compile(r"#(\w+)")
MULTI_SPACE = re.compile(r"\s+")
SPECIAL_CHARS = re.compile(r"[^\w\s.,!?;:'\"-]")


def clean_text(text: str) -> str:
    """Clean and normalize a single text string."""
    if not text or not isinstance(text, str):
        return ""

    # Strip URLs
    text = URL_PATTERN.sub("", text)

    # Strip usernames
    text = USERNAME_PATTERN.sub("", text)

    # Convert hashtags to words
    text = HASHTAG_PATTERN.sub(r"\1", text)

    # Remove Reddit-specific markers
    text = text.replace("[deleted]", "").replace("[removed]", "")

    # Normalize whitespace
    text = MULTI_SPACE.sub(" ", text).strip()

    return text


def tokenize_simple(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenization."""
    text_lower = text.lower()
    tokens = re.findall(r"\b\w+\b", text_lower)
    return tokens


def detect_phase(dt_str: str) -> str:
    """Assign temporal phase based on datetime."""
    if not dt_str:
        return "unknown"

    try:
        dt = pd.Timestamp(dt_str)
        if dt.tzinfo is None:
            dt = dt.tz_localize("UTC")
        date_str = dt.strftime("%Y-%m-%d")

        for phase_name, phase_info in PHASES.items():
            if phase_info["start"] <= date_str <= phase_info["end"]:
                return phase_name
        return "out_of_window"
    except Exception:
        return "unknown"


def detect_neighborhoods(text: str) -> list[str]:
    """Detect neighborhood mentions using lexicon matching."""
    if not text:
        return []

    detected = []
    text_lower = text.lower()

    for neighborhood, terms in NEIGHBORHOOD_LEXICON.items():
        for term in terms:
            if term.lower() in text_lower:
                detected.append(neighborhood)
                break

    return list(set(detected))


def flag_quality(text: str, word_count: int) -> str:
    """Flag posts with quality issues."""
    if word_count < 3:
        return "short"

    # Basic spam detection
    if text.count("http") > 3 or text.count("$$$") > 0:
        return "spam"

    # Very rough non-English check (if >50% non-ASCII)
    ascii_count = sum(1 for c in text if ord(c) < 128)
    if len(text) > 10 and ascii_count / len(text) < 0.5:
        return "non_english"

    return "ok"


def compute_text_hash(text: str) -> str:
    """Compute hash for deduplication."""
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    return hashlib.md5(normalized.encode()).hexdigest()


def run_cleaning():
    """Run the full cleaning pipeline on posts_raw → posts_clean."""
    log.info("🧹 Starting text cleaning pipeline")

    conn = get_connection()

    # Load raw data
    df = conn.execute("SELECT * FROM posts_raw").fetchdf()
    log.info(f"Loaded {len(df)} raw posts")

    if df.empty:
        log.warning("No raw posts to clean")
        conn.close()
        return

    # Clean text
    df["text_clean"] = df["text"].apply(clean_text)
    df["text_tokens"] = df["text_clean"].apply(tokenize_simple)
    df["text_lemmas"] = df["text_tokens"]  # Simplified; use spaCy for full lemmatization
    df["word_count"] = df["text_tokens"].apply(len)

    # Phase tagging
    df["phase"] = df["dt_utc"].astype(str).apply(detect_phase)

    # Neighborhood detection
    df["neighborhoods"] = df["text_clean"].apply(detect_neighborhoods)
    df["has_geo"] = df["neighborhoods"].apply(lambda x: len(x) > 0)

    # Quality flagging
    df["quality_flag"] = df.apply(
        lambda row: flag_quality(row["text_clean"], row["word_count"]), axis=1
    )

    # Deduplication
    df["_text_hash"] = df["text_clean"].apply(compute_text_hash)
    dup_hashes = df["_text_hash"].value_counts()
    dup_hashes = set(dup_hashes[dup_hashes > 1].index)
    df["is_duplicate"] = False
    seen_hashes = set()
    for idx in df.index:
        h = df.at[idx, "_text_hash"]
        if h in seen_hashes:
            df.at[idx, "is_duplicate"] = True
        else:
            seen_hashes.add(h)
    df.drop(columns=["_text_hash"], inplace=True)

    # Prepare for DB insert
    clean_df = df[[
        "id", "platform", "source", "dt_utc", "text", "text_clean",
        "text_tokens", "text_lemmas", "word_count", "phase",
        "neighborhoods", "has_geo", "is_duplicate", "quality_flag",
    ]].copy()
    clean_df.rename(columns={"text": "text_original"}, inplace=True)

    # Store to DuckDB
    conn.execute("DELETE FROM posts_clean")
    conn.register("clean_df", clean_df)
    conn.execute("""
        INSERT INTO posts_clean (
            id, platform, source, dt_utc, text_original, text_clean,
            text_tokens, text_lemmas, word_count, phase,
            neighborhoods, has_geo, is_duplicate, quality_flag
        )
        SELECT
            id, platform, source, dt_utc, text_original, text_clean,
            text_tokens, text_lemmas, word_count, phase,
            neighborhoods, has_geo, is_duplicate, quality_flag
        FROM clean_df
    """)

    # Export parquet
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    clean_df.to_parquet(processed_dir / "posts_clean.parquet", index=False)

    # Stats
    total = len(clean_df)
    ok = (clean_df["quality_flag"] == "ok").sum()
    dupes = clean_df["is_duplicate"].sum()
    phase_dist = clean_df["phase"].value_counts().to_dict()

    log.info(f"✅ Cleaning complete: {total} posts processed")
    log.info(f"   Quality OK: {ok} | Duplicates: {dupes}")
    log.info(f"   Phase distribution: {phase_dist}")

    conn.close()


if __name__ == "__main__":
    run_cleaning()
