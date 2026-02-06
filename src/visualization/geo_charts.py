"""Neighborhood-level geographic visualizations."""
import plotly.graph_objects as go
import pandas as pd
from src.utils.constants import TARGET_EMOTIONS

EMOTION_COLORS = {
    "fear": "#E74C3C", "anger": "#C0392B", "sadness": "#3498DB",
    "joy": "#F1C40F", "gratitude": "#2ECC71", "pride": "#E67E22",
}


def create_neighborhood_chart(geo_df: pd.DataFrame) -> go.Figure:
    if geo_df.empty:
        return go.Figure().update_layout(title="No geo-tagged data available")
    fig = go.Figure()
    key_emos = ["fear", "anger", "joy", "gratitude"]
    for emo in key_emos:
        col = f"{emo}_mean"
        if col in geo_df.columns:
            fig.add_trace(go.Bar(name=emo.capitalize(), x=geo_df["neighborhood"], y=geo_df[col],
                                 marker_color=EMOTION_COLORS.get(emo, "gray")))
    fig.update_layout(title="Emotion Intensity by Neighborhood", barmode="group",
                      template="plotly_white", height=450, yaxis_title="Mean Emotion Score",
                      annotations=[dict(text="⚠️ Geo-inference from text mentions; not GPS coordinates",
                                        xref="paper", yref="paper", x=0.5, y=-0.15, showarrow=False, font_size=10)])
    return fig


def create_geo_fear_timeline(df: pd.DataFrame) -> go.Figure:
    """Share of high-fear posts by neighborhood over phases."""
    if df.empty or "neighborhoods" not in df.columns:
        return go.Figure()
    geo_df = df[df["has_geo"] == True].copy()
    if geo_df.empty:
        return go.Figure()
    geo_df = geo_df.explode("neighborhoods")
    if "emo_fear" not in geo_df.columns:
        return go.Figure()
    geo_df["high_fear"] = geo_df["emo_fear"] > 0.3
    ct = pd.crosstab(geo_df["phase"], geo_df["neighborhoods"], values=geo_df["high_fear"],
                     aggfunc="mean").fillna(0)
    fig = go.Figure()
    for col in ct.columns:
        fig.add_trace(go.Scatter(x=ct.index, y=ct[col], mode="lines+markers", name=col))
    fig.update_layout(title="Share of High-Fear Posts by Neighborhood & Phase",
                      template="plotly_white", height=400, yaxis_title="Share (>0.3 fear)")
    return fig
