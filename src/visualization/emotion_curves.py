"""Plotly emotion trajectory charts with confidence bands and event overlays."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils.constants import EVENT_MARKERS, PHASES, TARGET_EMOTIONS

EMOTION_COLORS = {
    "fear": "#E74C3C",
    "anger": "#C0392B",
    "sadness": "#3498DB",
    "joy": "#F1C40F",
    "surprise": "#9B59B6",
    "disgust": "#1ABC9C",
    "gratitude": "#2ECC71",
    "pride": "#E67E22",
}
KEY_EMOTIONS = ["fear", "anger", "joy", "gratitude", "sadness", "pride"]


def create_emotion_trajectory_chart(daily_df, title="Emotion Trajectories Over Time"):
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.75, 0.25],
        subplot_titles=("Emotion Intensity", "Post Volume"),
    )
    for emo in KEY_EMOTIONS:
        col = f"{emo}_mean"
        if col in daily_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=daily_df["date"],
                    y=daily_df[col],
                    name=emo.capitalize(),
                    line=dict(color=EMOTION_COLORS[emo], width=2.5),
                    mode="lines+markers",
                    marker=dict(size=4),
                ),
                row=1,
                col=1,
            )
    if "n_posts" in daily_df.columns:
        fig.add_trace(
            go.Bar(
                x=daily_df["date"],
                y=daily_df["n_posts"],
                name="Posts",
                marker_color="rgba(100,100,100,0.4)",
            ),
            row=2,
            col=1,
        )
    for m in EVENT_MARKERS:
        fig.add_shape(
            type="line",
            x0=m["date"],
            x1=m["date"],
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color=m["color"], width=1.5, dash="dash"),
        )
        fig.add_annotation(
            x=m["date"],
            y=1.02,
            yref="paper",
            text=m["label"],
            showarrow=False,
            font=dict(size=9, color=m["color"]),
            textangle=-30,
        )
    fig.update_layout(
        title=title,
        height=650,
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x",
        hoverlabel=dict(bgcolor="#0e1117", font=dict(color="white"), bordercolor="#333"),
    )
    fig.update_yaxes(title_text="Mean Probability", row=1, col=1)
    fig.update_yaxes(title_text="# Posts", row=2, col=1)
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        legend=dict(bgcolor="#0e1117"),
    )
    return fig


def create_phase_comparison_chart(phase_df):
    fig = go.Figure()
    order = [p for p in PHASES if p in phase_df["phase"].values]
    labels = [PHASES[p]["label"] for p in order]
    for emo in KEY_EMOTIONS:
        col = f"{emo}_mean"
        if col not in phase_df.columns:
            continue
        vals, errs = [], []
        for p in order:
            r = phase_df[phase_df["phase"] == p]
            if not r.empty:
                vals.append(r[col].iloc[0])
                errs.append(r.get(f"{emo}_ci_hi", pd.Series([0])).iloc[0] - r[col].iloc[0])
        fig.add_trace(
            go.Bar(
                name=emo.capitalize(),
                x=labels[: len(vals)],
                y=vals,
                error_y=dict(type="data", array=errs, visible=True),
                marker_color=EMOTION_COLORS[emo],
            )
        )
    fig.update_layout(
        title="Emotion by Phase (95% CI)", barmode="group", template="plotly_dark", height=500
    )
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        legend=dict(bgcolor="#0e1117"),
    )
    return fig


def create_platform_contrast_chart(platform_df):
    fig = go.Figure()
    emos = KEY_EMOTIONS
    for _, row in platform_df.iterrows():
        vals = [row.get(f"{e}_mean", 0) for e in emos] + [row.get(f"{emos[0]}_mean", 0)]
        fig.add_trace(
            go.Scatterpolar(
                r=vals,
                theta=[e.capitalize() for e in emos] + [emos[0].capitalize()],
                name=row["platform"],
                fill="toself",
                opacity=0.6,
            )
        )
    fig.update_layout(
        title="Platform Emotion Profiles",
        polar=dict(radialaxis=dict(visible=True, range=[0, 0.5])),
        template="plotly_dark",
        height=500,
    )
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        legend=dict(bgcolor="#0e1117"),
    )
    return fig


def create_sentiment_heatmap(daily_df):
    cols = [f"{e}_mean" for e in TARGET_EMOTIONS if f"{e}_mean" in daily_df.columns]
    labels = [c.replace("_mean", "").capitalize() for c in cols]
    fig = go.Figure(
        data=go.Heatmap(
            z=daily_df[cols].values.T,
            x=daily_df["date"],
            y=labels,
            colorscale="RdYlGn_r",
            colorbar=dict(title="Intensity"),
        )
    )
    for m in EVENT_MARKERS:
        fig.add_shape(
            type="line",
            x0=m["date"],
            x1=m["date"],
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color=m["color"], width=1, dash="dash"),
        )
    fig.update_layout(title="Emotion Heatmap", template="plotly_dark", height=400)
    fig.update_layout(
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        legend=dict(bgcolor="#0e1117"),
    )
    return fig
