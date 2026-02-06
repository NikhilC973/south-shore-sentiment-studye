"""Plotly emotion trajectory charts with confidence bands and event overlays."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from src.utils.constants import TARGET_EMOTIONS, EVENT_MARKERS, PHASES

EMOTION_COLORS = {
    "fear": "#E74C3C", "anger": "#C0392B", "sadness": "#3498DB",
    "joy": "#F1C40F", "surprise": "#9B59B6", "disgust": "#1ABC9C",
    "gratitude": "#2ECC71", "pride": "#E67E22",
}
KEY_EMOTIONS = ["fear", "anger", "joy", "gratitude", "sadness", "pride"]


def create_emotion_trajectory_chart(daily_df: pd.DataFrame, title="Emotion Trajectories Over Time") -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        row_heights=[0.75, 0.25], subplot_titles=("Emotion Intensity", "Post Volume"))
    for emo in KEY_EMOTIONS:
        col = f"{emo}_mean"
        if col in daily_df.columns:
            fig.add_trace(go.Scatter(
                x=daily_df["date"], y=daily_df[col], name=emo.capitalize(),
                line=dict(color=EMOTION_COLORS[emo], width=2.5), mode="lines+markers", marker=dict(size=4),
            ), row=1, col=1)
    if "n_posts" in daily_df.columns:
        fig.add_trace(go.Bar(x=daily_df["date"], y=daily_df["n_posts"], name="Posts",
                             marker_color="rgba(100,100,100,0.4)"), row=2, col=1)
    for m in EVENT_MARKERS:
        fig.add_vline(x=m["date"], line_dash="dash", line_color=m["color"], line_width=1.5,
                      annotation_text=m["label"], annotation_position="top left", annotation_font_size=9)
    fig.update_layout(title=title, height=650, template="plotly_white",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), hovermode="x unified")
    fig.update_yaxes(title_text="Mean Probability", row=1, col=1)
    fig.update_yaxes(title_text="# Posts", row=2, col=1)
    return fig


def create_phase_comparison_chart(phase_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    order = [p for p in PHASES if p in phase_df["phase"].values]
    labels = [PHASES[p]["label"] for p in order]
    for emo in KEY_EMOTIONS:
        col = f"{emo}_mean"
        if col not in phase_df.columns: continue
        vals, errs = [], []
        for p in order:
            r = phase_df[phase_df["phase"] == p]
            if not r.empty:
                vals.append(r[col].iloc[0])
                errs.append(r.get(f"{emo}_ci_hi", pd.Series([0])).iloc[0] - r[col].iloc[0])
        fig.add_trace(go.Bar(name=emo.capitalize(), x=labels[:len(vals)], y=vals,
                             error_y=dict(type="data", array=errs, visible=True), marker_color=EMOTION_COLORS[emo]))
    fig.update_layout(title="Emotion by Phase (95% CI)", barmode="group", template="plotly_white", height=500)
    return fig


def create_platform_contrast_chart(platform_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    emos = KEY_EMOTIONS
    for _, row in platform_df.iterrows():
        vals = [row.get(f"{e}_mean", 0) for e in emos] + [row.get(f"{emos[0]}_mean", 0)]
        fig.add_trace(go.Scatterpolar(r=vals, theta=[e.capitalize() for e in emos] + [emos[0].capitalize()],
                                      name=row["platform"], fill="toself", opacity=0.6))
    fig.update_layout(title="Platform Emotion Profiles", polar=dict(radialaxis=dict(visible=True, range=[0, 0.5])),
                      template="plotly_white", height=500)
    return fig


def create_sentiment_heatmap(daily_df: pd.DataFrame) -> go.Figure:
    cols = [f"{e}_mean" for e in TARGET_EMOTIONS if f"{e}_mean" in daily_df.columns]
    labels = [c.replace("_mean", "").capitalize() for c in cols]
    fig = go.Figure(data=go.Heatmap(z=daily_df[cols].values.T, x=daily_df["date"], y=labels,
                                     colorscale="RdYlGn_r", colorbar=dict(title="Intensity")))
    for m in EVENT_MARKERS:
        fig.add_vline(x=m["date"], line_dash="dash", line_color=m["color"], line_width=1)
    fig.update_layout(title="Emotion Heatmap", template="plotly_white", height=400)
    return fig
