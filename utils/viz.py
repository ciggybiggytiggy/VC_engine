"""
Chart generation utilities — Maison Capital theme.
Bone white background, ink black axes, lacquer red accents.
Broadsheet-meets-Bloomberg aesthetic.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PLOT_BG    = "#FAFAF8"
PAPER_BG   = "#FAFAF8"
TEXT_COLOR = "#0A0A0A"
MUTED      = "#8A8480"
GRID_COLOR = "#E8E0D4"
AXIS_COLOR = "#4A4A4A"

PALETTE = [
    "#0A0A0A",   # ink
    "#C41E2A",   # lacquer
    "#4A4A4A",   # graphite
    "#8A8480",   # dust
    "#B8B4AE",   # fog
    "#A09890",   # rule-strong
    "#2C2C2C",   # ink-muted
    "#D4CEC6",   # rule
]

def _base_layout(title: str) -> dict:
    return dict(
        title=dict(
            text=title.upper(),
            font=dict(color=MUTED, size=8, family="Montserrat"),
            x=0,
            xanchor="left",
        ),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT_COLOR, family="Montserrat", size=11),
        margin=dict(l=20, r=20, t=44, b=20),
    )


def make_market_map(df: pd.DataFrame) -> go.Figure:
    if df.empty or "x" not in df.columns:
        return go.Figure()
    fig = px.scatter(
        df, x="x", y="y",
        color="sector",
        size="score" if "score" in df.columns else None,
        hover_data=["name", "funding_stage", "trend"],
        color_discrete_sequence=PALETTE,
    )
    fig.update_layout(
        **_base_layout("Market Map"),
        legend=dict(
            bgcolor="rgba(250,250,248,0.95)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(color=TEXT_COLOR, size=10),
            title=dict(text="SECTOR", font=dict(color=MUTED, size=8)),
        ),
        xaxis=dict(gridcolor=GRID_COLOR, color=AXIS_COLOR, zerolinecolor=GRID_COLOR,
                   tickfont=dict(color=MUTED), showline=True, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, color=AXIS_COLOR, zerolinecolor=GRID_COLOR,
                   tickfont=dict(color=MUTED), showline=True, linecolor=GRID_COLOR),
    )
    fig.update_traces(marker=dict(line=dict(width=0.5, color=PLOT_BG)))
    return fig


def make_deal_flow_bar(df_radar: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df_radar, x="deal_flow_score", y="name",
        color="predicted_investor",
        orientation="h",
        color_discrete_sequence=PALETTE,
        labels={"deal_flow_score": "Deal Flow Score", "name": ""},
    )
    fig.update_layout(
        **_base_layout("Deal Flow Radar"),
        yaxis=dict(autorange="reversed", gridcolor=GRID_COLOR,
                   tickfont=dict(color=TEXT_COLOR, size=10), color=TEXT_COLOR,
                   showline=True, linecolor=GRID_COLOR),
        xaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(color=MUTED), color=AXIS_COLOR,
                   showline=True, linecolor=GRID_COLOR),
        legend=dict(
            bgcolor="rgba(250,250,248,0.95)", bordercolor=GRID_COLOR, borderwidth=1,
            font=dict(color=TEXT_COLOR, size=9),
            title=dict(text="PREDICTED INVESTOR", font=dict(color=MUTED, size=8)),
        ),
        bargap=0.35,
    )
    fig.update_traces(marker=dict(line=dict(width=0, color=PLOT_BG)))
    return fig


def make_heatmap(heatmap_df: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        heatmap_df,
        color_continuous_scale=[
            [0,   "#F2EDE4"],
            [0.3, "#E8D4D0"],
            [0.6, "#D4818A"],
            [1.0, "#C41E2A"],
        ],
        aspect="auto",
        labels=dict(x="VC Fund", y="Startup", color="Likelihood"),
    )
    fig.update_layout(
        **_base_layout("VC Deal Heatmap — Investment Likelihood"),
        xaxis=dict(tickangle=-30, tickfont=dict(color=TEXT_COLOR, size=10), color=TEXT_COLOR),
        yaxis=dict(tickfont=dict(color=TEXT_COLOR, size=9), color=TEXT_COLOR),
        coloraxis_colorbar=dict(
            tickfont=dict(color=MUTED, size=9),
            title=dict(text="", font=dict(color=MUTED)),
            thickness=10,
            len=0.8,
        ),
    )
    return fig


def make_stage_donut(df: pd.DataFrame) -> go.Figure:
    if "funding_stage" not in df.columns:
        return go.Figure()
    counts = df["funding_stage"].value_counts().reset_index()
    counts.columns = ["stage", "count"]
    counts = counts[counts["stage"] != "Unknown"]
    fig = px.pie(
        counts, names="stage", values="count",
        hole=0.62,
        color_discrete_sequence=PALETTE,
    )
    fig.update_traces(
        textfont=dict(color=TEXT_COLOR, size=10, family="Figtree"),
        insidetextfont=dict(color=TEXT_COLOR),
        outsidetextfont=dict(color=MUTED),
        marker=dict(line=dict(color=PLOT_BG, width=2)),
    )
    fig.update_layout(
        **_base_layout("Stage Distribution"),
        showlegend=True,
        legend=dict(
            font=dict(color=TEXT_COLOR, size=10),
            bgcolor="rgba(250,250,248,0.95)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
        ),
        annotations=[dict(
            text="STAGE", x=0.5, y=0.5,
            font=dict(size=8, color=MUTED, family="Montserrat"),
            showarrow=False,
        )],
    )
    return fig


def make_trend_bar(df: pd.DataFrame) -> go.Figure:
    if "trend" not in df.columns:
        return go.Figure()
    all_trends = []
    for val in df["trend"].dropna():
        all_trends.extend([t.strip() for t in val.split(",") if t.strip()])
    if not all_trends:
        return go.Figure()
    trend_counts = pd.Series(all_trends).value_counts().head(10).reset_index()
    trend_counts.columns = ["trend", "count"]
    fig = px.bar(
        trend_counts, x="count", y="trend",
        orientation="h",
        color_discrete_sequence=["#C9A84C"],
    )
    fig.update_layout(
        **_base_layout("Trending Themes"),
        yaxis=dict(autorange="reversed", tickfont=dict(color=TEXT_COLOR, size=10),
                   color=TEXT_COLOR, gridcolor=GRID_COLOR, showline=True, linecolor=GRID_COLOR),
        xaxis=dict(tickfont=dict(color=MUTED), color=AXIS_COLOR, gridcolor=GRID_COLOR,
                   showline=True, linecolor=GRID_COLOR),
        bargap=0.3,
    )
    fig.update_traces(
        marker=dict(
            color=PALETTE[1],   # lacquer red
            line=dict(color=PLOT_BG, width=0),
            opacity=0.9,
        )
    )
    return fig