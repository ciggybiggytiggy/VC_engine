"""
A market analysis tool for identifying early-stage investment opportunities.
"""

import pandas as pd
import streamlit as st

# ------------------------------------------------------------------ #
#  Page config — must be first Streamlit call                         #
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="The C-Note",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ #
#  Imports                                                             #
# ------------------------------------------------------------------ #
from scrapers.fintech import scrape_fintech
from scrapers.healthcare import scrape_healthcare
from scrapers.consumer_retail import scrape_consumer_retail
from scrapers.operations_logistics import scrape_operations_logistics
from scrapers.marketing_social import scrape_marketing_social
from scrapers.tech import scrape_betalist, scrape_producthunt, scrape_yc
from scrapers.chicago import scrape_chicago

from utils.scoring import detect_funding_stage, label_trends, score_company, generate_rationale, is_chicago_area
from utils.snapshot import save_snapshot, compute_diff
from utils.export import export_csv, export_pdf
from utils.viz import make_market_map, make_deal_flow_bar, make_heatmap, make_stage_donut, make_trend_bar

# Legacy utils (portfolio overlap, semantic overlap, market map coords, deal flow radar, heatmap df)
from utils.utils import (
    deal_flow_radar,
    generate_deal_heatmap,
    clean_data,
    competitor_overlap,
    semantic_overlap,
    generate_market_map,
    portfolio_overlap,
)
from utils.portfolios import (
    get_chicago_ventures_portfolio,
    scrape_hyde_park_portfolio,
    scrape_m25_portfolio,
    scrape_origin_ventures,
)

# ------------------------------------------------------------------ #
#  Styling — Celine x Jane Street                                      #
#  Full obsidian dark mode. Champagne gold rules. Ice white type.      #
#  Fashion house precision meets quantitative trading terminal.        #
# ------------------------------------------------------------------ #
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400;1,600&family=IBM+Plex+Mono:wght@300;400;500;600&family=Neue+Haas+Grotesk+Display+Pro:wght@400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

  /* ─────────────────────────────────────────────────────────
     THE C-NOTE — Maison Capital
     Celine SS25 x Jane Street Terminal
     Obsidian. Champagne. Ice white. Absolute precision.
  ───────────────────────────────────────────────────────── */
  :root {
    --void:        #080808;
    --obsidian:    #0D0D0D;
    --obsidian-2:  #111111;
    --obsidian-3:  #161616;
    --obsidian-4:  #1C1C1C;
    --obsidian-5:  #222222;
    --smoke:       #2A2A2A;
    --graphite:    #3A3A3A;
    --iron:        #555555;
    --steel:       #777777;
    --silver:      #9A9A9A;
    --fog:         #C0C0C0;
    --ice:         #E8E8E8;
    --white:       #F5F5F5;

    --gold:        #C9A84C;
    --gold-lt:     #E2C476;
    --gold-dk:     #8A6E2A;
    --gold-muted:  #7A6235;
    --gold-dim:    rgba(201,168,76,0.15);
    --gold-glow:   rgba(201,168,76,0.06);

    --signal:      #4AE0A0;
    --signal-dim:  rgba(74,224,160,0.12);

    --rule:        rgba(201,168,76,0.18);
    --rule-strong: rgba(201,168,76,0.35);
    --rule-hard:   rgba(201,168,76,0.55);
  }

  /* ── Base ── */
  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stApp"] {
    background-color: var(--void) !important;
    font-family: 'Space Grotesk', sans-serif !important;
  }

  /* Subtle grain texture on the background */
  [data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
    background-size: 200px 200px;
    pointer-events: none;
    z-index: 0;
    opacity: 0.6;
  }

  /* ── Main content pane ── */
  [data-testid="stMainBlockContainer"],
  [data-testid="block-container"] {
    background: var(--obsidian-2) !important;
    border-radius: 0 !important;
    padding: 3rem 4rem !important;
    border: none !important;
    border-left: 1px solid var(--rule) !important;
    border-right: 1px solid var(--rule) !important;
    box-shadow:
      0 0 0 1px rgba(201,168,76,0.06),
      0 40px 120px rgba(0,0,0,0.8),
      inset 0 1px 0 rgba(201,168,76,0.08) !important;
    position: relative !important;
    z-index: 1 !important;
  }

  /* Gold top rule — the signature mark */
  [data-testid="stMainBlockContainer"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
      transparent 0%,
      var(--gold) 20%,
      var(--gold-lt) 50%,
      var(--gold) 80%,
      transparent 100%
    );
    opacity: 0.8;
  }

  /* ── Global text ── */
  [data-testid="stMainBlockContainer"],
  [data-testid="stMainBlockContainer"] p,
  [data-testid="stMainBlockContainer"] span,
  [data-testid="stMainBlockContainer"] div,
  [data-testid="stMainBlockContainer"] label,
  [data-testid="stMainBlockContainer"] li {
    color: var(--fog) !important;
    font-family: 'Space Grotesk', sans-serif !important;
  }

  /* ── Typography ── */
  h1 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 300 !important;
    font-size: 4rem !important;
    letter-spacing: 0.04em !important;
    color: var(--white) !important;
    line-height: 0.95 !important;
    margin-bottom: 0.08em !important;
    text-transform: uppercase !important;
  }
  h2 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 400 !important;
    font-size: 2rem !important;
    color: var(--white) !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
  }
  h3 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 400 !important;
    font-size: 0.62rem !important;
    color: var(--gold) !important;
    letter-spacing: 0.28em !important;
    text-transform: uppercase !important;
  }
  h4 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 500 !important;
    font-size: 1.15rem !important;
    color: var(--ice) !important;
    letter-spacing: 0.02em !important;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: var(--void) !important;
    border-right: 1px solid var(--rule) !important;
  }
  [data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
  }
  [data-testid="stSidebar"] *,
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div {
    color: var(--steel) !important;
    font-family: 'Space Grotesk', sans-serif !important;
  }
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2 {
    color: var(--white) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 400 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-size: 1.5rem !important;
  }
  [data-testid="stSidebar"] h3 {
    color: var(--gold) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.58rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.28em !important;
    text-transform: uppercase !important;
  }
  [data-testid="stSidebar"] label {
    color: var(--iron) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.58rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
  }
  [data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--fog) !important;
    border: 1px solid var(--rule-strong) !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 400 !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    padding: 12px 20px !important;
    transition: all 0.25s ease !important;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: var(--gold-dim) !important;
    color: var(--gold-lt) !important;
    border-color: var(--gold) !important;
  }
  [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: var(--obsidian-3) !important;
    border: 1px solid var(--smoke) !important;
    border-radius: 0 !important;
    color: var(--fog) !important;
  }
  [data-testid="stSidebar"] hr {
    border-top: 1px solid var(--rule) !important;
  }

  /* ── Metric cards ── */
  [data-testid="metric-container"] {
    background: var(--obsidian-3) !important;
    border: none !important;
    border-top: 1px solid var(--rule-hard) !important;
    border-radius: 0 !important;
    padding: 20px 24px 18px !important;
    box-shadow:
      0 1px 0 rgba(201,168,76,0.05),
      inset 0 0 40px rgba(201,168,76,0.02) !important;
    position: relative !important;
    transition: border-color 0.2s !important;
  }
  [data-testid="metric-container"]:hover {
    border-top-color: var(--gold-lt) !important;
  }
  [data-testid="metric-container"] label {
    color: var(--iron) !important;
    font-size: 0.55rem !important;
    font-weight: 400 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.26em !important;
    font-family: 'IBM Plex Mono', monospace !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--white) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 3.2rem !important;
    font-weight: 300 !important;
    line-height: 1 !important;
    letter-spacing: -0.01em !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: var(--gold) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
  }

  /* ── Section headers ── */
  .section-header {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.55rem !important;
    font-weight: 400 !important;
    color: var(--gold) !important;
    padding: 0 0 12px 0 !important;
    border-bottom: 1px solid var(--rule) !important;
    margin-bottom: 28px !important;
    letter-spacing: 0.3em !important;
    text-transform: uppercase !important;
    display: flex !important;
    align-items: center !important;
    gap: 14px !important;
  }
  .section-header::before {
    content: '';
    display: inline-block;
    width: 24px;
    height: 1px;
    background: linear-gradient(90deg, var(--gold), transparent);
    flex-shrink: 0;
  }
  .section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--rule), transparent);
    margin-left: auto;
  }

  /* ── Pick cards ── */
  .pick-card {
    background: transparent;
    border: none;
    border-top: 1px solid var(--rule);
    border-radius: 0;
    padding: 24px 0;
    margin-bottom: 0;
    transition: all 0.25s ease;
    position: relative;
  }
  .pick-card + .pick-card { border-top: none; }
  .pick-card::before {
    content: '';
    position: absolute;
    left: -4rem;
    top: 0; bottom: 0;
    width: 0;
    background: var(--gold-glow);
    transition: width 0.3s ease;
  }
  .pick-card:hover::before {
    width: calc(100% + 8rem);
  }
  .pick-card:hover {
    border-top-color: var(--rule-strong);
  }
  .pick-card h4 {
    margin: 0 0 8px 0 !important;
    color: var(--white) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.35rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    line-height: 1.2 !important;
    position: relative;
  }
  .pick-card h4 a {
    color: var(--white) !important;
    text-decoration: none !important;
    border-bottom: 1px solid var(--gold-muted) !important;
    padding-bottom: 1px !important;
    transition: border-color 0.2s, color 0.2s !important;
  }
  .pick-card h4 a:hover {
    color: var(--gold-lt) !important;
    border-bottom-color: var(--gold-lt) !important;
  }
  .pick-card p {
    margin: 6px 0 0 0 !important;
    color: var(--steel) !important;
    font-size: 0.8rem !important;
    line-height: 1.7 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 400 !important;
    position: relative;
  }

  /* ── Badges ── */
  .badge {
    display: inline-block;
    background: transparent;
    color: var(--iron) !important;
    border-radius: 0;
    padding: 2px 8px;
    font-size: 0.5rem;
    font-weight: 400;
    margin-right: 5px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    border: 1px solid var(--smoke);
    font-family: 'IBM Plex Mono', monospace !important;
    transition: all 0.2s;
  }
  .badge-green {
    background: transparent !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold-muted) !important;
  }
  .badge-orange {
    background: var(--gold-dim) !important;
    color: var(--gold-lt) !important;
    border: 1px solid var(--gold) !important;
    font-weight: 600 !important;
  }

  /* ── New tag ── */
  .new-tag {
    background: transparent;
    color: var(--signal) !important;
    border: 1px solid var(--signal) !important;
    border-radius: 0;
    padding: 1px 7px;
    font-size: 0.48rem;
    font-weight: 400;
    margin-left: 8px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    font-family: 'IBM Plex Mono', monospace !important;
  }

  /* ── Data tables ── */
  [data-testid="stDataFrame"] {
    border: none !important;
    border-top: 1px solid var(--gold) !important;
    border-radius: 0 !important;
    overflow: hidden !important;
  }
  [data-testid="stDataFrame"] table {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    background: var(--obsidian-2) !important;
  }
  [data-testid="stDataFrame"] th {
    background: var(--obsidian-4) !important;
    color: var(--gold) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.5rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid var(--rule) !important;
  }
  [data-testid="stDataFrame"] td {
    background: transparent !important;
    color: var(--fog) !important;
    border-bottom: 1px solid rgba(201,168,76,0.06) !important;
  }
  [data-testid="stDataFrame"] tr:hover td {
    background: var(--gold-glow) !important;
  }

  /* ── Expanders ── */
  [data-testid="stExpander"] {
    border: none !important;
    border-top: 1px solid var(--rule) !important;
    border-radius: 0 !important;
    background: transparent !important;
  }
  [data-testid="stExpander"] summary {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.58rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--iron) !important;
    transition: color 0.2s !important;
  }
  [data-testid="stExpander"] summary:hover {
    color: var(--gold) !important;
  }

  /* ── HR dividers ── */
  hr {
    border: none !important;
    border-top: 1px solid var(--rule) !important;
    margin: 3rem 0 !important;
  }

  /* ── Alerts / status ── */
  [data-testid="stAlert"] {
    background: var(--obsidian-4) !important;
    border: 1px solid var(--rule) !important;
    border-left: 2px solid var(--gold) !important;
    border-radius: 0 !important;
    color: var(--fog) !important;
  }

  [data-testid="stStatusWidget"] {
    background: var(--obsidian-3) !important;
    border: 1px solid var(--rule) !important;
    border-top: 1px solid var(--gold) !important;
    border-radius: 0 !important;
    color: var(--fog) !important;
  }

  /* ── Inputs ── */
  [data-testid="stSelectbox"] > div > div,
  [data-testid="stMultiSelect"] > div > div {
    background: var(--obsidian-3) !important;
    border: 1px solid var(--smoke) !important;
    border-radius: 0 !important;
    color: var(--fog) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.8rem !important;
  }
  [data-testid="stSelectbox"] > div > div:focus-within,
  [data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px var(--gold-dim) !important;
  }

  [data-testid="stTextInput"] input {
    background: var(--obsidian-3) !important;
    border: 1px solid var(--smoke) !important;
    border-radius: 0 !important;
    color: var(--fog) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.8rem !important;
    padding: 10px 14px !important;
  }
  [data-testid="stTextInput"] input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px var(--gold-dim) !important;
  }

  /* ── Buttons ── */
  .stButton > button[kind="primary"],
  button[data-testid="baseButton-primary"] {
    background: transparent !important;
    color: var(--gold-lt) !important;
    border: 1px solid var(--gold) !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 400 !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.28em !important;
    text-transform: uppercase !important;
    padding: 14px 28px !important;
    transition: all 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
  }
  .stButton > button[kind="primary"]::before,
  button[data-testid="baseButton-primary"]::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--gold-dim);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.25s ease;
  }
  .stButton > button[kind="primary"]:hover::before,
  button[data-testid="baseButton-primary"]:hover::before {
    transform: scaleX(1);
  }
  .stButton > button[kind="primary"]:hover,
  button[data-testid="baseButton-primary"]:hover {
    color: var(--gold-lt) !important;
    border-color: var(--gold-lt) !important;
    box-shadow: 0 0 20px var(--gold-dim) !important;
  }

  .stDownloadButton > button {
    background: transparent !important;
    color: var(--steel) !important;
    border: 1px solid var(--smoke) !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 400 !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    transition: all 0.25s ease !important;
  }
  .stDownloadButton > button:hover {
    background: var(--obsidian-4) !important;
    color: var(--gold) !important;
    border-color: var(--gold-muted) !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 3px; height: 3px; }
  ::-webkit-scrollbar-track { background: var(--void); }
  ::-webkit-scrollbar-thumb { background: var(--smoke); border-radius: 0; }
  ::-webkit-scrollbar-thumb:hover { background: var(--gold-muted); }

  /* ── Chart container ── */
  [data-testid="stPlotlyChart"] {
    border-top: 1px solid var(--rule) !important;
    padding-top: 10px !important;
    background: transparent !important;
  }

  /* ── Captions ── */
  [data-testid="stCaptionContainer"] p,
  .stCaption p {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.62rem !important;
    color: var(--iron) !important;
    letter-spacing: 0.08em !important;
  }

  /* ── Multiselect tags ── */
  [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: var(--obsidian-5) !important;
    border: 1px solid var(--rule) !important;
    border-radius: 0 !important;
    color: var(--gold) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.58rem !important;
  }

  /* ── Spinner / loading ── */
  [data-testid="stSpinner"] {
    color: var(--gold) !important;
  }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ #
#  Portfolio data (cached — no need to re-scrape on every run)        #
# ------------------------------------------------------------------ #
@st.cache_data(ttl=86400, show_spinner=False)
def load_portfolios():
    # Chicago Ventures portfolio is hardcoded — always accurate, no scraping needed
    chicago = get_chicago_ventures_portfolio()
    return {
        "my_portfolio": chicago,
        "competitor_portfolios": {
            "Chicago Ventures": chicago,
            "Hyde Park Ventures": scrape_hyde_park_portfolio(),
            "M25": scrape_m25_portfolio(),
            "Origin Ventures": scrape_origin_ventures(),
        },
    }


@st.cache_data(ttl=1800, show_spinner=False)
def run_pipeline(industry_key: str, scraper_name: str):
    """Run the full scraping + analysis pipeline. Cached for 30 min."""

    scraper_map = {
        "fintech": scrape_fintech,
        "tech": (scrape_betalist, scrape_producthunt),
        "edgar_form_filings": scrape_yc,
        "healthcare": scrape_healthcare,
        "consumer_retail_fashion": scrape_consumer_retail,
        "operations_logistics": scrape_operations_logistics,
        "marketing_social": scrape_marketing_social,
        "chicago": scrape_chicago,
    }

    portfolios = load_portfolios()
    chicago_portfolio = portfolios["my_portfolio"]
    competitor_portfolios = portfolios["competitor_portfolios"]

    scraper_fn = scraper_map[scraper_name]
    if isinstance(scraper_fn, tuple):
        raw_dfs = [fn() for fn in scraper_fn]
    else:
        raw_dfs = [scraper_fn()]

    df = clean_data(raw_dfs)
    if df.empty:
        return df, {}, competitor_portfolios

    # Portfolio flag (fix: boolean column, not sparse name column)
    df["is_portfolio"] = df["name"].isin(chicago_portfolio.keys())
    df["is_chicago"] = df.apply(is_chicago_area, axis=1)

    if "amount_raised" not in df.columns:
      df["amount_raised"] = ""
    if "state" not in df.columns:
      df["state"] = ""

    # Stage + trend
    df["funding_stage"] = df.apply(detect_funding_stage, axis=1)
    df["trend"] = df.apply(label_trends, axis=1)

    # Filter noise — keep everything with a signal, plus up to 50 unknowns
    # so the UI always has data to display
    has_signal = (
        (df["funding_stage"] != "Unknown") |
        (df["trend"] != "") |
        (df["is_portfolio"])
    )
    df = pd.concat(
        [df[has_signal], df[~has_signal].head(50)]
    ).drop_duplicates().reset_index(drop=True)

    if df.empty:
        return df, {}, competitor_portfolios

    # Semantic overlap
    df = semantic_overlap(df, chicago_portfolio)

    # Scoring
    df["score"] = df.apply(score_company, axis=1)

    # Competitor overlap (called once — was duplicated in original)
    df = competitor_overlap(df, competitor_portfolios)

    # Market map coordinates
    df = generate_market_map(df)

    # Deal flow radar
    df = deal_flow_radar(df, competitor_portfolios)
    df["deal_flow_score"] = df["portfolio_overlap_score"] * df["competitor_overlap_score"]

    # Human-readable rationale
    df["rationale"] = df.apply(generate_rationale, axis=1)

    # Save snapshot + compute diff
    save_snapshot(df, industry_key)
    diff = compute_diff(df, industry_key)

    return df, diff, competitor_portfolios


# ------------------------------------------------------------------ #
#  Sidebar                                                             #
# ------------------------------------------------------------------ #
with st.sidebar:
    st.markdown("## The C-Note")
    st.markdown("*Catherine's Deal Flow Intelligence*")
    st.markdown("---")

    INDUSTRIES = {
        "fintech": ("Fintech", "fintech"),
        "tech": ("Tech", "tech"),
        "edgar_form_filings": ("Edgar Form Filings", "edgar_form_filings"),
        "healthcare": ("Healthcare", "healthcare"),
        "consumer_retail_fashion": ("CPG", "consumer_retail_fashion"),
        "operations_logistics": ("Operations / Logistics", "operations_logistics"),
        "marketing_social": ("Marketing / Social", "marketing_social"),
        "chicago": ("Chicago Startups", "chicago")

    }

    selected_label = st.selectbox(
        "Industry",
        options=[v[0] for v in INDUSTRIES.values()],
    )
    selected_key = [k for k, v in INDUSTRIES.items() if v[0] == selected_label][0]
    selected_scraper = INDUSTRIES[selected_key][1]
       
    if "last_industry" not in st.session_state:
        st.session_state.last_industry = selected_key

    if st.session_state.last_industry != selected_key:
        st.cache_data.clear()
        st.session_state.last_industry = selected_key

    st.markdown("---")
    st.markdown("### Fund Settings")
    fund_name = st.text_input("Fund Name", value="Chicago Ventures")
    analyst_name = st.text_input("Analyst Name", value="")
    st.markdown("---")
    st.markdown("### Filters")
    stage_filter = st.multiselect(
        "Funding Stage",
        options=["Pre-Seed", "Seed", "Series A", "Series B", "Series C+", "Growth", "Unknown"],
        default=[],
        placeholder="All stages (no filter)",
    )

    run_btn = st.button("Run Analysis", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("""
    <p style="color:#2A2A2A; font-size:.6rem; line-height:1.9; font-family:'IBM Plex Mono',monospace; letter-spacing:.06em">
    Built by <span style="color:#555">Catherine Walker</span><br>
    Tracking pre-seed &amp; seed in Fintech,<br>Health, and B2B SaaS<br>
    <span style="color:#3A3A3A">Chicago-area focus</span>
    </p>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------ #
#  Main Content -- header                                            #
# ------------------------------------------------------------------ #
st.markdown("## The C-Note - {industry}".format(industry=selected_label))
st.markdown('<div class="section-header"> The who, the how, the why — today’s market pulse in under 5 minutes </div>', unsafe_allow_html=True)

if not run_btn:
    st.markdown("""
    <div style="border:1px solid rgba(201,168,76,0.2); border-left:1px solid rgba(201,168,76,0.6); 
    background:rgba(201,168,76,0.04); padding:32px 36px; margin-bottom:2.5rem">
    <p style="color:#C9A84C; font-size:.52rem; font-weight:400; font-family:'IBM Plex Mono',monospace;
    letter-spacing:.3em; text-transform:uppercase; margin:0 0 14px 0">
    — Signal Over Noise</p>
    <p style="color:#C8C8C8; font-size:1.1rem; line-height:1.85; margin:0; font-family:'Cormorant Garamond',serif; font-weight:400; letter-spacing:0.01em">
    Early startup signals appear across fragmented sources long before companies show up in traditional deal databases.
    This platform aggregates signals like SEC Form D filings, Show HN launches, and founder RSS feeds to surface potential deals earlier in the sourcing pipeline.
    </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="border-top:1px solid rgba(201,168,76,0.55); background:#111; 
        padding:24px 28px;">
        <p style="color:#C9A84C; font-size:2.8rem; font-weight:300; 
        font-family:'Cormorant Garamond',serif; margin:0; line-height:1; letter-spacing:-0.01em">6</p>
        <p style="color:#555; font-size:.5rem; font-weight:400; font-family:'IBM Plex Mono',monospace;
        letter-spacing:.26em; text-transform:uppercase; margin:10px 0 0 0">
        Data Sources</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="border-top:1px solid rgba(201,168,76,0.55); background:#111; 
        padding:24px 28px;">
        <p style="color:#C9A84C; font-size:2.8rem; font-weight:300; 
        font-family:'Cormorant Garamond',serif; margin:0; line-height:1; letter-spacing:-0.01em">4</p>
        <p style="color:#555; font-size:.5rem; font-weight:400; font-family:'IBM Plex Mono',monospace;
        letter-spacing:.26em; text-transform:uppercase; margin:10px 0 0 0">
        VC Portfolios Tracked</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="border-top:1px solid rgba(201,168,76,0.55); background:#111; 
        padding:24px 28px;">
        <p style="color:#C9A84C; font-size:2.8rem; font-weight:300; 
        font-family:'Cormorant Garamond',serif; margin:0; line-height:1; letter-spacing:-0.01em">30m</p>
        <p style="color:#555; font-size:.5rem; font-weight:400; font-family:'IBM Plex Mono',monospace;
        letter-spacing:.26em; text-transform:uppercase; margin:10px 0 0 0">
        Cache Refresh</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#3A3A3A; font-size:.7rem; line-height:1.9; font-family:'IBM Plex Mono',monospace; letter-spacing:.04em">
    <span style="color:#555">SOURCES —</span> SEC EDGAR Form D &nbsp;·&nbsp; Hacker News Show HN &nbsp;·&nbsp; TechCrunch Funding &nbsp;·&nbsp; Crunchbase News &nbsp;·&nbsp; Built In Chicago &nbsp;·&nbsp; Product Hunt<br>
    <span style="color:#555">PORTFOLIOS —</span> Chicago Ventures &nbsp;·&nbsp; Hyde Park Angels &nbsp;·&nbsp; M25 &nbsp;·&nbsp; Origin Ventures
    </p>
    """, unsafe_allow_html=True)
    st.stop()

# ── Run pipeline with progress indicator ── #
status = st.status("Running my analysis…", expanded=True)
with status:
    st.write("Looking for the next $10B valuation…")
    df, diff, competitor_portfolios = run_pipeline(selected_key, selected_scraper)
    st.write("Convincing the data to behave…")
    st.write("Scoring & labeling…")
    st.write("Saving snapshot…")
status.update(label="Analysis complete", state="complete", expanded=False)

if df.empty:
    st.warning("No data returned. The scraped sources may be blocking requests or have changed structure.")
    st.stop()

# ── Stage filter ── #
if stage_filter:
    df_filtered = df[df["funding_stage"].isin(stage_filter)]
else:
    df_filtered = df

# ------------------------------------------------------------------ #
#  Weekly Diff Banner                                                  #
# ------------------------------------------------------------------ #
if diff.get("has_previous"):
    prev_date = diff["previous_date"]
    n_new = len(diff["new_companies"])
    n_stage = len(diff["stage_changes"])
 
    st.markdown('<div class="section-header"> What\'s New Since Last Run</div>', unsafe_allow_html=True)
 
    d1, d2, d3 = st.columns(3)
    d1.metric("New Companies", n_new)
    d2.metric("Stage Changes", n_stage)
    d3.metric("Compared To", prev_date)
 
    if n_new > 0 and not diff["new_companies"].empty:
        new_df = diff["new_companies"].copy()
        new_cols = ["name", "source", "funding_stage", "amount_raised", "is_chicago", "trend", "rationale", "score"]
        available_new = [c for c in new_cols if c in new_df.columns]
        st.dataframe(new_df[available_new].reset_index(drop=True), use_container_width=True)
    else:
        st.caption("No new companies since last run.")
 
    if not diff["stage_changes"].empty:
        with st.expander(f"{n_stage} Stage Changes"):
            st.dataframe(diff["stage_changes"], use_container_width=True)
 
    st.markdown("---")
# ------------------------------------------------------------------ #
#  KPI metrics row                                                     #
# ------------------------------------------------------------------ #
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Total Companies", len(df))
m2.metric("Seed or Earlier", len(df[df["funding_stage"].isin(["Pre-Seed", "Seed"])]))
m3.metric("Chicago-Area", len(df[df["is_chicago"]]) if "is_chicago" in df.columns else "—")
m4.metric("With Trend Signal", len(df[df["trend"] != ""]))
m5.metric("Portfolio Matches", len(df[df["is_portfolio"]]))
m6.metric("Avg Score", f"{df['score'].mean():.1f}" if "score" in df.columns else "—")
 

# ------------------------------------------------------------------ #
#  Top 5 Picks                                                         #
# ------------------------------------------------------------------ #

st.markdown('<div class="section-header"> Catherine\'s Top 5 of The Week</div>', unsafe_allow_html=True)
st.markdown("""
<p style="color:#3A3A3A; font-size:.62rem; margin:-8px 0 20px 0; font-family:'IBM Plex Mono',monospace; letter-spacing:.08em">
Ranked by composite score — funding stage · thesis alignment ·
Chicago geography · portfolio proximity · competitor overlap
</p>
""", unsafe_allow_html=True)
 
top5 = df_filtered.nlargest(5, "score").reset_index(drop=True) if "score" in df_filtered.columns else df_filtered.head(5)
 
for i, row in top5.iterrows():
    stage = row.get("funding_stage", "")
    trend = row.get("trend", "")
    rationale = row.get("rationale", "")
    score = row.get("score", "")
    name = row.get("name", "Unknown")
    url = row.get("url", "")
    source = row.get("source", "")
    amount = row.get("amount_raised", "")
    chicago = row.get("is_chicago", False)
 
    stage_class = "badge-green" if stage in ("Pre-Seed", "Seed") else "badge-orange" if stage == "Series A" else "badge"
    name_html = f'<a href="{url}" target="_blank">{name}</a>' if url else name
 
    badges = f'<span class="badge {stage_class}">{stage}</span>' if stage else ""
    if chicago:
        badges += '<span class="badge badge-green">Chicago</span>'
    if amount:
        badges += f'<span class="badge">{amount}</span>'
    if trend:
        for t in trend.split(",")[:2]:
            badges += f'<span class="badge">{t.strip()}</span>'
 
    source_line = f'<p style="color:#3A3A3A;font-size:.58rem;margin-top:8px;font-family:IBM Plex Mono,monospace;letter-spacing:.1em;text-transform:uppercase;">via {source}</p>' if source else ""
 
    st.markdown(f"""
    <div class="pick-card">
      <h4>#{i+1} {name_html} &nbsp; {badges}</h4>
      <p>{rationale}</p>
      <p style="color:#555;font-size:.6rem;margin-top:8px;font-family:'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;">Score &nbsp;<span style="color:#C9A84C">{score}</span></p>
      {source_line}
    </div>
    """, unsafe_allow_html=True)
 
 
# ------------------------------------------------------------------ #
#  Charts — row 1                                                      #
# ------------------------------------------------------------------ #
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-header"> Stage Distribution</div>', unsafe_allow_html=True)
    st.plotly_chart(make_stage_donut(df_filtered), use_container_width=True, key="stage_donut")

with col_right:
    st.markdown('<div class="section-header"> Current Market Trending Themes</div>', unsafe_allow_html=True)
    st.plotly_chart(make_trend_bar(df_filtered), use_container_width=True, key="trend_bar")

# ------------------------------------------------------------------ #
#  Deal Flow Radar                                                     #
# ------------------------------------------------------------------ #
 
st.markdown('<div class="section-header"> Deal Flow Radar </div>', unsafe_allow_html=True)
st.markdown("""
<p style="color:#3A3A3A; font-size:.62rem; margin:-8px 0 20px 0; font-family:'IBM Plex Mono',monospace; letter-spacing:.08em">
Companies ranked by portfolio × competitor overlap — highest risk of losing to another fund
</p>
""", unsafe_allow_html=True)
 
radar_cols = ["name", "source", "funding_stage", "amount_raised", "is_chicago",
              "trend", "predicted_investor", "deal_flow_score", "rationale"]
available_radar = [c for c in radar_cols if c in df_filtered.columns]
df_radar = df_filtered.nlargest(8, "deal_flow_score")[available_radar].reset_index(drop=True)
df_radar.insert(0, "Rank", range(1, len(df_radar) + 1))
 
col_tbl, col_chart = st.columns([1, 1])
with col_tbl:
    display_radar = ["Rank", "name", "source", "funding_stage", "amount_raised",
                     "predicted_investor", "deal_flow_score"]
    st.dataframe(
        df_radar[[c for c in display_radar if c in df_radar.columns]],
        use_container_width=True,
    )
with col_chart:
    st.plotly_chart(make_deal_flow_bar(df_radar), use_container_width=True, key="deal_flow_bar")
# ------------------------------------------------------------------ #
#  VC Heatmap                                                          #
# ------------------------------------------------------------------ #
st.markdown('<div class="section-header"> Deal Heatmap</div>', unsafe_allow_html=True)
heatmap_df = generate_deal_heatmap(df_filtered, competitor_portfolios)
if not heatmap_df.empty:
    st.plotly_chart(make_heatmap(heatmap_df), use_container_width=True, key="vc_heatmap")

# ------------------------------------------------------------------ #
#  Market Map                                                          #
# ------------------------------------------------------------------ #
st.markdown('<div class="section-header"> Market Map</div>', unsafe_allow_html=True)
if "x" in df_filtered.columns and "y" in df_filtered.columns:
    st.plotly_chart(make_market_map(df_filtered), use_container_width=True, key="market_map")

# ------------------------------------------------------------------ #
#  Seed Spotlight & Trending Tables                                    #
# ------------------------------------------------------------------ #
col_seed, col_trend = st.columns(2)

with col_seed:
    st.markdown('<div class="section-header"> Seed Stage Spotlight</div>', unsafe_allow_html=True)
    df_seed = df_filtered[df_filtered["funding_stage"].isin(["Pre-Seed", "Seed"])].head(8)
    show_cols = ["name", "source", "funding_stage", "amount_raised", "is_chicago", "trend", "rationale", "score"]
    st.dataframe(df_seed[[c for c in show_cols if c in df_seed.columns]].reset_index(drop=True), use_container_width=True)

with col_trend:
    st.markdown('<div class="section-header"> Trending Now</div>', unsafe_allow_html=True)
    df_trending = df_filtered[(df_filtered["trend"] != "") & (df_filtered["trend"].notna())].head(8)
    st.dataframe(df_trending[[c for c in show_cols if c in df_trending.columns]].reset_index(drop=True), use_container_width=True)

# ------------------------------------------------------------------ #
#  Portfolio Overlap                                                   #
# ------------------------------------------------------------------ #
st.markdown('<div class="section-header"> Highest Portfolio Overlap</div>', unsafe_allow_html=True)

overlap_cols = ["name", "source", "funding_stage", "amount_raised", "is_chicago",
                "trend", "portfolio_overlap_score", "closest_portfolio_company",
                "competitor_overlap_score", "rationale"]

df_overlap = df_filtered.nlargest(8, "portfolio_overlap_score")[[c for c in overlap_cols if c in df_filtered.columns]].reset_index(drop=True)
st.dataframe(df_overlap, use_container_width=True)

# ------------------------------------------------------------------ #
#  Full dataset expander                                               #
# ------------------------------------------------------------------ #
with st.expander("Raw Dataset"):
    st.dataframe(df_filtered, use_container_width=True)

# ------------------------------------------------------------------ #
#  Exports                                                             #
# ------------------------------------------------------------------ #
st.markdown("---")
st.markdown('<div class="section-header"> Export</div>', unsafe_allow_html=True)
exp_col1, exp_col2, _ = st.columns([1, 1, 2])

with exp_col1:
    csv_bytes = export_csv(df_filtered)
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=f"deal_flow_{selected_key}.csv",
        mime="text/csv",
        use_container_width=True,
    )

with exp_col2:
    pdf_bytes = export_pdf(df_filtered, selected_label, fund_name=fund_name, analyst_name=analyst_name)
    st.download_button(
        label="Download PDF Memo",
        data=pdf_bytes,
        file_name=f"deal_memo_{selected_key}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )