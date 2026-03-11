import json

import streamlit as st

import pandas as pd
import plotly.express as px

from scrapers.fintech import scrape_fintech
from scrapers.healthcare import scrape_healthcare
from scrapers.consumer_retail import scrape_consumer_retail
from scrapers.operations_logistics import scrape_operations_logistics
from scrapers.marketing_social import scrape_marketing_social
from scrapers.tech import scrape_betalist, scrape_producthunt

from utils.utils import deal_flow_radar, generate_deal_heatmap, clean_data, competitor_overlap, detect_funding_stage, label_trends, score_company, portfolio_overlap, generate_market_map, save_snapshot, generate_memo, semantic_overlap
from utils.portfolios import scrape_chicago_ventures_portfolio, scrape_hyde_park_portfolio, scrape_m25_portfolio, scrape_origin_ventures

st.set_page_config(layout="wide")
st.title("What's New")

chicago_ventures_portfolio = scrape_chicago_ventures_portfolio()

competitor_portfolios = {
    "Chicago Ventures": chicago_ventures_portfolio,
    "Hyde Park Ventures": scrape_hyde_park_portfolio(),
    "M25": scrape_m25_portfolio(),
    "Origin Ventures": scrape_origin_ventures(),
}


# Industry selection dropdown
INDUSTRIES = {
    'fintech': ('Fintech', scrape_fintech),
    'tech': ('Tech', scrape_betalist, scrape_producthunt),
    'healthcare': ('Healthcare', scrape_healthcare),
    'consumer_retail_fashion': ('Consumer Retail / Fashion / Ecommerce', scrape_consumer_retail),
    'operations_logistics': ('Operations / Logistics', scrape_operations_logistics),
    'marketing_social': ('Marketing / Social', scrape_marketing_social)
}

industry_display = [v[0] for v in INDUSTRIES.values()]
selected_industry_display = st.selectbox("Select Industry:", industry_display)

# Find the corresponding scraper function and key
selected_industry_key = [k for k, v in INDUSTRIES.items() if v[0] == selected_industry_display][0]
scraper_func = [v[1] for v in INDUSTRIES.values() if v[0] == selected_industry_display][0]

if st.button("Run Scraper"):
    df_all = scraper_func()

    df = clean_data([df_all])

    df["company"] = df[df["name"].isin(chicago_ventures_portfolio.keys())]["name"]

    df["funding_stage"] = df.apply(detect_funding_stage, axis=1)
    df["trend"] = df.apply(label_trends, axis=1)

    # Filter to only companies with detected funding, trending topics, or portfolio match
    df = df[(df['funding_stage'] != 'Unknown') | (df['trend'] != '') | (df['company'].notna())]

    df = semantic_overlap(df, chicago_ventures_portfolio)
    
    df["score"] = df.apply(score_company, axis=1)

    df = competitor_overlap(df, competitor_portfolios)
    df = competitor_overlap(df, competitor_portfolios)

    df = generate_market_map(df)

    save_snapshot(df)

    df_seed = df[df['funding_stage'].isin(['Pre-Seed', 'Seed'])].head(5).reset_index(drop=True)
    df_seed['rank'] = range(1, len(df_seed) + 1)
    df_trending = df[(df['trend'] != '') & (df['trend'].notna())].head(5).reset_index(drop=True)
    df_trending['rank'] = range(1, len(df_trending) + 1)

    df = deal_flow_radar(df, competitor_portfolios)

    df["deal_flow_score"] = (df["portfolio_overlap_score"] * df["competitor_overlap_score"])

    st.subheader("Deal Flow Radar")

    df_radar = df.nlargest(
        5,
        "deal_flow_score"
    )[[
        "name",
        "funding_stage",
        "trend",
        "predicted_investor",
        "deal_flow_score"
    ]].reset_index(drop=True)

    df_radar["rank"] = range(1, len(df_radar)+1)

    st.dataframe(df_radar)

    fig_radar = px.bar(
    df_radar,
    x="deal_flow_score",
    y="name",
    color="predicted_investor",
    orientation="h",
    title="Deal Flow Radar - Likely Next Investor"
    )

    st.plotly_chart(fig_radar)

    heatmap_df = generate_deal_heatmap(df, competitor_portfolios)

    st.subheader("VC Deal Heatmap")

    fig_heatmap = px.imshow(
        heatmap_df,
        color_continuous_scale="Blues",
        aspect="auto",
        labels=dict(x="VC Fund", y="Startup", color="Investment Likelihood")
    )

    st.plotly_chart(fig_heatmap)

        

    st.subheader("Recent Seed Funding to Watch")
    st.dataframe(df_seed)

    st.subheader("Current Trending")
    st.dataframe(df_trending)

    fig = px.scatter(df, x="x", y="y", color="sector",
                     hover_data=["name", "funding_stage"])
    st.plotly_chart(fig)

    df_highest_overlap = df.nlargest(5, 'portfolio_overlap_score')[['name', 'funding_stage', 'trend', 'portfolio_overlap_score', 'closest_portfolio_company','competitor_overlap_score']].reset_index(drop=True)
    df_highest_overlap['rank'] = range(1, len(df_highest_overlap) + 1)
    
    st.subheader(f"Highest Portfolio Overlap - {selected_industry_key.replace('_', ' ').title()}")
    st.dataframe(df_highest_overlap)
