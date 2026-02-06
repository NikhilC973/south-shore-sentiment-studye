"""Topic visualization charts."""
import plotly.graph_objects as go
import pandas as pd


def create_topic_distribution_chart(topic_df: pd.DataFrame) -> go.Figure:
    counts = topic_df["topic_label"].value_counts().head(15)
    fig = go.Figure(go.Bar(x=counts.values, y=counts.index, orientation="h",
                           marker_color="steelblue"))
    fig.update_layout(title="Top 15 Discussion Topics", template="plotly_white",
                      height=500, xaxis_title="Number of Posts", yaxis=dict(autorange="reversed"))
    return fig


def create_topic_phase_heatmap(df: pd.DataFrame) -> go.Figure:
    if "phase" not in df.columns or "topic_label" not in df.columns:
        return go.Figure()
    ct = pd.crosstab(df["topic_label"], df["phase"], normalize="columns")
    top_topics = ct.sum(axis=1).nlargest(10).index
    ct = ct.loc[ct.index.isin(top_topics)]
    fig = go.Figure(data=go.Heatmap(z=ct.values, x=ct.columns, y=ct.index,
                                     colorscale="Blues", colorbar=dict(title="Share")))
    fig.update_layout(title="Topic Prevalence by Phase", template="plotly_white", height=450)
    return fig
