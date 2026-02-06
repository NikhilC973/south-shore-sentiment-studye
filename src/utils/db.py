"""
DuckDB connection manager and schema initialization.
"""
import duckdb
from pathlib import Path
from src.utils.constants import PROJECT_ROOT
from src.utils.logger import log


DB_PATH = PROJECT_ROOT / "data" / "sentiment_study.duckdb"


def get_connection(db_path: Path | str | None = None) -> duckdb.DuckDBPyConnection:
    """Get a DuckDB connection. Creates the file if it doesn't exist."""
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(path))
    return conn


def init_database(db_path: Path | str | None = None) -> None:
    """Initialize database with all required tables."""
    conn = get_connection(db_path)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts_raw (
            id              VARCHAR PRIMARY KEY,
            platform        VARCHAR NOT NULL,         -- 'reddit' | 'news_comment'
            source          VARCHAR,                  -- subreddit name or news domain
            url             VARCHAR,
            dt_utc          TIMESTAMP WITH TIME ZONE,
            text            VARCHAR,
            title           VARCHAR,                  -- for Reddit submissions
            author_display  VARCHAR,
            score           INTEGER DEFAULT 0,
            like_count      INTEGER DEFAULT 0,
            reply_count     INTEGER DEFAULT 0,
            share_count     INTEGER DEFAULT 0,
            parent_id       VARCHAR,                  -- for comments/replies
            post_type       VARCHAR,                  -- 'submission' | 'comment'
            detected_locs   VARCHAR[],                -- neighborhood mentions
            anchors         VARCHAR,                  -- 'pre' | 'event' | 'post_week1' etc.
            search_term     VARCHAR,                  -- query that found this post
            collected_at    TIMESTAMP DEFAULT now()
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts_clean (
            id              VARCHAR PRIMARY KEY,
            platform        VARCHAR,
            source          VARCHAR,
            dt_utc          TIMESTAMP WITH TIME ZONE,
            text_original   VARCHAR,
            text_clean      VARCHAR,                  -- normalized text
            text_tokens     VARCHAR[],                -- tokenized
            text_lemmas     VARCHAR[],                -- lemmatized
            word_count      INTEGER,
            phase           VARCHAR,                  -- temporal phase
            neighborhoods   VARCHAR[],                -- detected neighborhood tags
            has_geo         BOOLEAN DEFAULT false,
            is_duplicate    BOOLEAN DEFAULT false,
            quality_flag    VARCHAR DEFAULT 'ok'      -- 'ok' | 'short' | 'spam' | 'non_english'
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts_emotions (
            id                  VARCHAR PRIMARY KEY,
            -- VADER scores
            vader_compound      FLOAT,
            vader_positive      FLOAT,
            vader_negative      FLOAT,
            vader_neutral       FLOAT,
            -- RoBERTa sentiment
            roberta_positive    FLOAT,
            roberta_negative    FLOAT,
            roberta_neutral     FLOAT,
            -- GoEmotions (target 8)
            emo_fear            FLOAT,
            emo_anger           FLOAT,
            emo_sadness         FLOAT,
            emo_joy             FLOAT,
            emo_surprise        FLOAT,
            emo_disgust         FLOAT,
            emo_gratitude       FLOAT,
            emo_pride           FLOAT,
            -- Derived
            dominant_emotion    VARCHAR,
            emotion_confidence  FLOAT,
            sentiment_label     VARCHAR                -- 'positive' | 'negative' | 'neutral'
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts_topics (
            id              VARCHAR PRIMARY KEY,
            topic_id        INTEGER,
            topic_label     VARCHAR,
            topic_prob      FLOAT,
            top_terms       VARCHAR[]
        );
    """)

    # Convenience view joining all tables
    conn.execute("""
        CREATE OR REPLACE VIEW posts_full AS
        SELECT
            c.*,
            e.vader_compound, e.vader_positive, e.vader_negative, e.vader_neutral,
            e.roberta_positive, e.roberta_negative, e.roberta_neutral,
            e.emo_fear, e.emo_anger, e.emo_sadness, e.emo_joy,
            e.emo_surprise, e.emo_disgust, e.emo_gratitude, e.emo_pride,
            e.dominant_emotion, e.emotion_confidence, e.sentiment_label,
            t.topic_id, t.topic_label, t.topic_prob, t.top_terms
        FROM posts_clean c
        LEFT JOIN posts_emotions e ON c.id = e.id
        LEFT JOIN posts_topics t ON c.id = t.id
        WHERE c.is_duplicate = false
          AND c.quality_flag = 'ok';
    """)

    conn.close()
    log.info(f"✅ Database initialized at {db_path or DB_PATH}")


def query_df(sql: str, db_path: Path | str | None = None):
    """Execute SQL and return a Pandas DataFrame."""
    conn = get_connection(db_path)
    try:
        return conn.execute(sql).fetchdf()
    finally:
        conn.close()


def execute(sql: str, params=None, db_path: Path | str | None = None):
    """Execute SQL statement."""
    conn = get_connection(db_path)
    try:
        if params:
            conn.execute(sql, params)
        else:
            conn.execute(sql)
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
