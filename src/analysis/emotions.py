"""
GoEmotions Multi-Label Emotion Analysis.

Maps 27 GoEmotions labels to 8 target emotions:
fear, anger, sadness, joy, surprise, disgust, gratitude, pride.
"""
import pandas as pd
from src.utils.db import get_connection, init_database
from src.utils.constants import PROJECT_ROOT, GOEMOTIONS_MAP, TARGET_EMOTIONS
from src.utils.logger import log

_emotion_pipeline = None


def _get_pipeline():
    global _emotion_pipeline
    if _emotion_pipeline is None:
        from transformers import pipeline
        _emotion_pipeline = pipeline(
            "text-classification",
            model="monologg/bert-base-cased-goemotions-original",
            tokenizer="monologg/bert-base-cased-goemotions-original",
            max_length=512, truncation=True, top_k=None,
        )
        log.info("GoEmotions pipeline loaded")
    return _emotion_pipeline


def score_emotions_batch(texts: list[str], batch_size: int = 32) -> list[dict]:
    pipe = _get_pipeline()
    results = []
    for i in range(0, len(texts), batch_size):
        batch = [t if t and isinstance(t, str) and len(t.strip()) > 0 else "neutral" for t in texts[i:i+batch_size]]
        try:
            preds = pipe(batch)
            for pred in preds:
                scores = {e: 0.0 for e in TARGET_EMOTIONS}
                if isinstance(pred, list):
                    for item in pred:
                        target = GOEMOTIONS_MAP.get(item["label"].lower())
                        if target and target in scores:
                            scores[target] = max(scores[target], item["score"])
                results.append(scores)
        except Exception as e:
            log.warning(f"GoEmotions batch error: {e}")
            results.extend([{e: 0.0 for e in TARGET_EMOTIONS}] * len(batch))
    return results


def determine_dominant(scores: dict, threshold: float = 0.3) -> tuple[str, float]:
    if not scores:
        return "neutral", 0.0
    top = max(scores, key=scores.get)
    return (top, scores[top]) if scores[top] >= threshold else ("neutral", scores[top])


def run_emotion_analysis():
    log.info("Starting GoEmotions analysis")
    init_database()
    conn = get_connection()
    df = conn.execute(
        "SELECT id, text_clean FROM posts_clean WHERE is_duplicate=false AND quality_flag='ok'"
    ).fetchdf()

    if df.empty:
        log.warning("No posts to analyze"); conn.close(); return

    log.info(f"Scoring {len(df)} posts")
    try:
        emo_scores = score_emotions_batch(df["text_clean"].tolist())
    except Exception as e:
        log.error(f"GoEmotions failed: {e}. Using VADER fallback.")
        from src.analysis.sentiment import score_vader
        emo_scores = []
        for t in df["text_clean"]:
            v = score_vader(t)["compound"]
            s = {e: 0.0 for e in TARGET_EMOTIONS}
            if v < -0.3:
                s["fear"], s["anger"], s["sadness"] = abs(v)*0.5, abs(v)*0.3, abs(v)*0.2
            elif v > 0.3:
                s["joy"], s["gratitude"], s["pride"] = v*0.4, v*0.3, v*0.3
            emo_scores.append(s)

    for emo in TARGET_EMOTIONS:
        df[f"emo_{emo}"] = [s.get(emo, 0.0) for s in emo_scores]

    dominant = [determine_dominant(s) for s in emo_scores]
    df["dominant_emotion"] = [d[0] for d in dominant]
    df["emotion_confidence"] = [d[1] for d in dominant]

    existing = set(conn.execute("SELECT id FROM posts_emotions").fetchdf()["id"]) if \
        conn.execute("SELECT COUNT(*) FROM posts_emotions").fetchone()[0] > 0 else set()

    for _, r in df.iterrows():
        vals = [r[f"emo_{e}"] for e in TARGET_EMOTIONS] + [r["dominant_emotion"], r["emotion_confidence"]]
        if r["id"] in existing:
            conn.execute(
                f"UPDATE posts_emotions SET {', '.join(f'emo_{e}=?' for e in TARGET_EMOTIONS)}, "
                "dominant_emotion=?, emotion_confidence=? WHERE id=?",
                vals + [r["id"]]
            )
        else:
            conn.execute(
                f"INSERT INTO posts_emotions (id, {', '.join(f'emo_{e}' for e in TARGET_EMOTIONS)}, "
                "dominant_emotion, emotion_confidence) VALUES (?" + ", ?" * (len(TARGET_EMOTIONS)+2) + ")",
                [r["id"]] + vals
            )

    out = PROJECT_ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / "emotion_scores.parquet", index=False)
    log.info(f"Emotion analysis complete: {df['dominant_emotion'].value_counts().to_dict()}")
    conn.close()


if __name__ == "__main__":
    run_emotion_analysis()
