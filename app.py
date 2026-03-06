import json

import streamlit as st
import pandas as pd
import plotly.express as px

from scrapers.fintech import scrape_fintech
from scrapers.healthcare import scrape_healthcare
from scrapers.consumer_retail import scrape_consumer_retail
from scrapers.operations_logistics import scrape_operations_logistics
from scrapers.marketing_social import scrape_marketing_social

from utils.utils import clean_data, detect_funding_stage, label_trends, score_company, portfolio_overlap, generate_market_map, save_snapshot, generate_memo
from utils.portfolios import chicago_ventures_portfolio

st.set_page_config(layout="wide")
st.title("What's New")


# Industry selection dropdown
INDUSTRIES = {
    'fintech': ('Fintech', scrape_fintech),
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

    df = portfolio_overlap(df, chicago_ventures_portfolio)
    df["score"] = df.apply(score_company, axis=1)

    df = generate_market_map(df)

    save_snapshot(df)

    df_seed = df[df['funding_stage'].isin(['Pre-Seed', 'Seed'])].head(5).reset_index(drop=True)
    df_seed['rank'] = range(1, len(df_seed) + 1)
    df_trending = df[(df['trend'] != '') & (df['trend'].notna())].head(5).reset_index(drop=True)
    df_trending['rank'] = range(1, len(df_trending) + 1)

    st.subheader("Recent Seed Funding to Watch")
    st.dataframe(df_seed)

    st.subheader("Current Trending")
    st.dataframe(df_trending)

    fig = px.scatter(df, x="x", y="y", color="sector",
                     hover_data=["name", "funding_stage"])
    st.plotly_chart(fig)

    df_highest_overlap = df.nlargest(5, 'portfolio_overlap_score')[['name', 'funding_stage', 'trend', 'portfolio_overlap_score', 'closest_portfolio_company']].reset_index(drop=True)
    df_highest_overlap['rank'] = range(1, len(df_highest_overlap) + 1)
    
    st.subheader(f"Highest Portfolio Overlap - {selected_industry_key.replace('_', ' ').title()}")
    st.dataframe(df_highest_overlap)
