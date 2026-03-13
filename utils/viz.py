"""
Chart generation utilities — Maison Capital dark theme.
Obsidian base, champagne gold accents, ice white text.
Celine x Jane Street aesthetic.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PLOT_BG    = "#0D0D0D"
PAPER_BG   = "#0D0D0D"
TEXT_COLOR = "#C0C0C0"
MUTED      = "#555555"
GRID_COLOR = "rgba(201,168,76,0.1)"
AXIS_COLOR = "#3A3A3A"
GOLD       = "#C9A84C"
GOLD_LT    = "#E2C476"

PALETTE = [
    "#C9A84C",   # gold
    "#E2C476",   # gold light
    "#E8E8E8",   # ice white
    "#777777",   # steel
    "#4AE0A0",   # signal green
    "#9A9A9A",   # silver
    "#3A3A3A",   # graphite
    "#1C1C1C",   # obsidian
]

def _base_layout(title: str) -> dict:
    return dict(
        title=dict(
            text=title.upper(),
            font=dict(color=GOLD, size=7, family="IBM Plex Mono"),
            x=0,
            xanchor="left",
        ),
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(color=TEXT_COLOR, family="Space Grotesk", size=11),
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
            bgcolor="rgba(13,13,13,0.95)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(color=TEXT_COLOR, size=10),
            title=dict(text="SECTOR", font=dict(color=GOLD, size=7, family="IBM Plex Mono")),
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
            bgcolor="rgba(13,13,13,0.95)", bordercolor=GRID_COLOR, borderwidth=1,
            font=dict(color=TEXT_COLOR, size=9),
            title=dict(text="PREDICTED INVESTOR", font=dict(color=GOLD, size=7, family="IBM Plex Mono")),
        ),
        bargap=0.35,
    )
    fig.update_traces(marker=dict(line=dict(width=0, color=PLOT_BG)))
    return fig


def make_heatmap(heatmap_df: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        heatmap_df,
        color_continuous_scale=[
            [0,   "#111111"],
            [0.2, "#1A1508"],
            [0.5, "#5A420E"],
            [0.75, "#997020"],
            [1.0, "#C9A84C"],
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
            thickness=8,
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
        textfont=dict(color=TEXT_COLOR, size=10, family="Space Grotesk"),
        insidetextfont=dict(color=TEXT_COLOR),
        outsidetextfont=dict(color=MUTED),
        marker=dict(line=dict(color=PLOT_BG, width=2)),
    )
    fig.update_layout(
        **_base_layout("Stage Distribution"),
        showlegend=True,
        legend=dict(
            font=dict(color=TEXT_COLOR, size=10),
            bgcolor="rgba(13,13,13,0.95)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
        ),
        annotations=[dict(
            text="STAGE", x=0.5, y=0.5,
            font=dict(size=7, color=GOLD, family="IBM Plex Mono"),
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
            color=GOLD,
            line=dict(color=PLOT_BG, width=0),
            opacity=0.85,
        )
    )
    return fig