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
#  Styling — Cheetah Print Editorial Theme                             #
# ------------------------------------------------------------------ #
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,700;0,900;1,400;1,700&family=DM+Mono:wght@300;400;500&family=Montserrat:wght@300;400;500;600;700&display=swap');

  /* ─────────────────────────────────────────────────────────
     THE C-NOTE — Maison Capital
     Bottega Veneta x Bloomberg Terminal
     Bone. Ink. Lacquer red. Nothing else.
  ───────────────────────────────────────────────────────── */
  :root {
    --bone:        #F2EDE4;
    --bone-deep:   #E8E0D4;
    --parchment:   #EDE6DA;
    --ink:         #0A0A0A;
    --ink-soft:    #1A1A1A;
    --ink-muted:   #2C2C2C;
    --graphite:    #4A4A4A;
    --dust:        #8A8480;
    --fog:         #B8B4AE;
    --lacquer:     #C41E2A;
    --lacquer-dk:  #8B1520;
    --lacquer-lt:  #E8424F;
    --carbon:      #0F0F0F;
    --panel:       #F7F3EC;
    --rule:        #D4CEC6;
    --rule-strong: #A09890;
    --white:       #FAFAF8;
  }

  /* ── Base: bone white, like heavy stock paper ── */
  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stApp"] {
    background-color: var(--bone) !important;
    font-family: 'Montserrat', sans-serif !important;
  }

  /* ── Subtle halftone grain on the background ── */
  [data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      radial-gradient(circle at 1px 1px, rgba(10,10,10,0.04) 1px, transparent 0);
    background-size: 24px 24px;
    pointer-events: none;
    z-index: 0;
  }

  /* ── Main content: clean white sheet laid over parchment ── */
  [data-testid="stMainBlockContainer"],
  [data-testid="block-container"] {
    background: var(--white) !important;
    border-radius: 0 !important;
    padding: 3rem 4rem !important;
    border: none !important;
    border-left: 1px solid var(--rule) !important;
    border-right: 1px solid var(--rule) !important;
    box-shadow: 0 1px 0 var(--rule), 0 40px 80px rgba(10,10,10,0.08) !important;
    position: relative !important;
    z-index: 1 !important;
  }

  /* ── The red rule at top — like a luxury masthead ── */
  [data-testid="stMainBlockContainer"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--lacquer);
  }

  /* ── All text defaults ── */
  [data-testid="stMainBlockContainer"],
  [data-testid="stMainBlockContainer"] p,
  [data-testid="stMainBlockContainer"] span,
  [data-testid="stMainBlockContainer"] div,
  [data-testid="stMainBlockContainer"] label,
  [data-testid="stMainBlockContainer"] li {
    color: var(--ink) !important;
    font-family: 'Montserrat', sans-serif !important;
  }

  /* ── Display headings — editorial Playfair ── */
  h1 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 900 !important;
    font-size: 3.2rem !important;
    letter-spacing: -0.02em !important;
    color: var(--ink) !important;
    line-height: 1.0 !important;
    margin-bottom: 0.1em !important;
  }
  h2 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
    color: var(--ink) !important;
    letter-spacing: -0.01em !important;
  }
  h3 {
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    color: var(--graphite) !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
  }
  h4 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 500 !important;
    font-size: 1.1rem !important;
    color: var(--ink) !important;
    letter-spacing: 0 !important;
  }

  /* ── Sidebar — deep ink, like a book spine ── */
  [data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: none !important;
  }

  /* Fine red rule at top of sidebar */
  [data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--lacquer);
  }

  [data-testid="stSidebar"] *,
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div {
    color: var(--fog) !important;
    font-family: 'Montserrat', sans-serif !important;
  }

  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 {
    color: var(--bone) !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    text-transform: none !important;
    font-size: 1.4rem !important;
  }

  [data-testid="stSidebar"] label {
    color: var(--dust) !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
  }

  [data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--bone) !important;
    border: 1px solid rgba(242,237,228,0.2) !important;
    border-radius: 0 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 12px 20px !important;
    transition: all 0.2s ease !important;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: var(--lacquer) !important;
    color: var(--white) !important;
    border-color: var(--lacquer) !important;
  }

  /* Sidebar selectbox */
  [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 0 !important;
    color: var(--bone) !important;
  }

  /* ── Metric cards — ticker-board style ── */
  [data-testid="metric-container"] {
    background: var(--panel) !important;
    border: none !important;
    border-top: 2px solid var(--ink) !important;
    border-radius: 0 !important;
    padding: 20px 24px 18px !important;
    box-shadow: none !important;
    position: relative !important;
  }
  [data-testid="metric-container"] label {
    color: var(--dust) !important;
    font-size: 0.58rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.2em !important;
    font-family: 'Montserrat', sans-serif !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 2.8rem !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    letter-spacing: -0.03em !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: var(--lacquer) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
  }

  /* ── Section headers — WSJ-style column labels ── */
  .section-header {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.58rem !important;
    font-weight: 700 !important;
    color: var(--dust) !important;
    padding: 0 0 10px 0 !important;
    border-bottom: 1px solid var(--ink) !important;
    margin-bottom: 24px !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
  }
  .section-header::before {
    content: '';
    display: inline-block;
    width: 18px;
    height: 2px;
    background: var(--lacquer);
    flex-shrink: 0;
  }

  /* ── Pick cards — editorial article cards ── */
  .pick-card {
    background: var(--white);
    border: none;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    border-radius: 0;
    padding: 22px 0;
    margin-bottom: 0;
    transition: all 0.2s ease;
    position: relative;
  }
  .pick-card + .pick-card {
    border-top: none;
  }
  .pick-card:hover {
    background: var(--panel);
    padding-left: 16px;
    padding-right: 16px;
    margin-left: -16px;
    margin-right: -16px;
  }
  .pick-card h4 {
    margin: 0 0 6px 0 !important;
    color: var(--ink) !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    line-height: 1.3 !important;
  }
  .pick-card h4 a {
    color: var(--ink) !important;
    text-decoration: none !important;
    border-bottom: 1px solid var(--lacquer) !important;
    padding-bottom: 1px !important;
  }
  .pick-card h4 a:hover {
    color: var(--lacquer) !important;
  }
  .pick-card p {
    margin: 4px 0 0 0 !important;
    color: var(--graphite) !important;
    font-size: 0.82rem !important;
    line-height: 1.6 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 400 !important;
  }

  /* ── Badges — tight mono labels ── */
  .badge {
    display: inline-block;
    background: transparent;
    color: var(--graphite) !important;
    border-radius: 0;
    padding: 2px 7px;
    font-size: 0.55rem;
    font-weight: 600;
    margin-right: 5px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    border: 1px solid var(--rule-strong);
    font-family: 'Montserrat', sans-serif !important;
  }
  .badge-green {
    background: transparent !important;
    color: var(--ink) !important;
    border: 1px solid var(--ink) !important;
  }
  .badge-orange {
    background: var(--lacquer) !important;
    color: var(--white) !important;
    border: 1px solid var(--lacquer) !important;
    font-weight: 700 !important;
  }

  /* ── New-tag pill ── */
  .new-tag {
    background: var(--lacquer);
    color: var(--white) !important;
    border-radius: 0;
    padding: 2px 7px;
    font-size: 0.55rem;
    font-weight: 700;
    margin-left: 8px;
    border: none;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-family: 'Montserrat', sans-serif !important;
  }

  /* ── DataFrames — broadsheet table ── */
  [data-testid="stDataFrame"] {
    border: none !important;
    border-top: 2px solid var(--ink) !important;
    border-radius: 0 !important;
    overflow: hidden !important;
  }
  [data-testid="stDataFrame"] table {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
  }
  [data-testid="stDataFrame"] th {
    background: var(--ink) !important;
    color: var(--bone) !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.58rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 10px 14px !important;
  }

  /* ── Expanders ── */
  [data-testid="stExpander"] {
    border: none !important;
    border-top: 1px solid var(--rule) !important;
    border-radius: 0 !important;
    background: transparent !important;
  }
  [data-testid="stExpander"] summary {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--graphite) !important;
  }

  /* ── Horizontal rule ── */
  hr {
    border: none !important;
    border-top: 1px solid var(--rule) !important;
    margin: 2.5rem 0 !important;
  }

  /* ── Alerts ── */
  [data-testid="stAlert"] {
    background: var(--panel) !important;
    border: none !important;
    border-left: 3px solid var(--lacquer) !important;
    border-radius: 0 !important;
    color: var(--ink) !important;
  }

  /* ── Status widget ── */
  [data-testid="stStatusWidget"] {
    background: var(--panel) !important;
    border: 1px solid var(--rule) !important;
    border-top: 2px solid var(--lacquer) !important;
    border-radius: 0 !important;
  }

  /* ── Selectbox / multiselect ── */
  [data-testid="stSelectbox"] > div > div,
  [data-testid="stMultiSelect"] > div > div {
    background: var(--white) !important;
    border: 1px solid var(--rule-strong) !important;
    border-radius: 0 !important;
    color: var(--ink) !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.82rem !important;
  }
  [data-testid="stSelectbox"] > div > div:focus-within,
  [data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: var(--ink) !important;
    box-shadow: none !important;
  }

  /* ── Text inputs ── */
  [data-testid="stTextInput"] input {
    background: var(--white) !important;
    border: 1px solid var(--rule-strong) !important;
    border-radius: 0 !important;
    color: var(--ink) !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.82rem !important;
    padding: 10px 14px !important;
  }
  [data-testid="stTextInput"] input:focus {
    border-color: var(--ink) !important;
    box-shadow: none !important;
  }

  /* ── Primary button (Run Analysis) ── */
  .stButton > button[kind="primary"],
  button[data-testid="baseButton-primary"] {
    background: var(--ink) !important;
    color: var(--bone) !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    padding: 14px 28px !important;
    transition: all 0.2s ease !important;
  }
  .stButton > button[kind="primary"]:hover,
  button[data-testid="baseButton-primary"]:hover {
    background: var(--lacquer) !important;
    color: var(--white) !important;
  }

  /* ── Download buttons ── */
  .stDownloadButton > button {
    background: transparent !important;
    color: var(--ink) !important;
    border: 1px solid var(--ink) !important;
    border-radius: 0 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
  }
  .stDownloadButton > button:hover {
    background: var(--ink) !important;
    color: var(--bone) !important;
  }

  /* ── Scrollbar — thin, elegant ── */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: var(--bone-deep); }
  ::-webkit-scrollbar-thumb { background: var(--rule-strong); border-radius: 0; }
  ::-webkit-scrollbar-thumb:hover { background: var(--lacquer); }

  /* ── Plotly chart containers ── */
  [data-testid="stPlotlyChart"] {
    border-top: 1px solid var(--rule) !important;
    padding-top: 8px !important;
  }

  /* ── Caption / small text ── */
  [data-testid="stCaptionContainer"] p,
  .stCaption p {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    color: var(--dust) !important;
    letter-spacing: 0.02em !important;
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
    raw_df = scraper_fn()

    df = clean_data([raw_df])
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

      # ── TEMPORARY DEBUG — replace previous debug block in sidebar ── #

    if st.button("Debug Sources", use_container_width=True):
        import requests
        import xml.etree.ElementTree as ET
        from datetime import datetime, timedelta

        HEADERS = {"User-Agent": "Mozilla/5.0"}

        st.markdown("### Source Debug")

        # 1. RSS feeds — test new sources too
        feeds = [
            ("https://www.builtinchicago.org/feed",          "Built In Chicago (alt)"),
            ("https://www.chicagobusiness.com/rss/news",      "Crain's Chicago"),
            ("https://news.crunchbase.com/feed/",             "Crunchbase News"),
            ("https://techcrunch.com/tag/funding/feed/",      "TechCrunch Funding"),
            ("https://www.finsmes.com/feed",                  "FinSMEs"),
            ("https://www.geekwire.com/feed/",                "GeekWire"),
        ]
        for url, name in feeds:
            try:
                r = requests.get(url, headers=HEADERS, timeout=8)
                if r.ok:
                    try:
                        root = ET.fromstring(r.content)
                        items = root.findall(".//item")
                        st.write(f"✓ {name}: {r.status_code}, {len(items)} items")
                    except:
                        st.write(f"✓ {name}: {r.status_code}, XML parse error")
                else:
                    st.write(f"✗ {name}: {r.status_code}")
            except Exception as e:
                st.write(f"✗ {name}: {str(e)[:80]}")

        # 2. EDGAR — show exactly what comes back
        st.markdown("---")
        st.markdown("**EDGAR Raw:**")
        try:
            start = (datetime.today() - timedelta(days=60)).strftime("%Y-%m-%d")
            r = requests.get(
                "https://efts.sec.gov/LATEST/search-index",
                headers={"User-Agent": "deal-flow-tool contact@test.com"},
                params={"q": '"Chicago"', "dateRange": "custom",
                        "startdt": start, "forms": "D"},
                timeout=12,
            )
            st.write(f"Status: {r.status_code}")
            if r.ok:
                data = r.json()
                hits = data.get("hits", {}).get("hits", [])
                total = data.get("hits", {}).get("total", {})
                st.write(f"Total: {total} | Returned: {len(hits)}")
                if hits:
                    st.write("First hit:", hits[0])
                else:
                    st.write("Full response:", data)
            else:
                st.write("Body:", r.text[:300])
        except Exception as e:
            st.write(f"Error: {e}")

        # 3. EDGAR with wider date and no quotes
        st.markdown("**EDGAR wider search (Illinois, no quotes, 180d):**")
        try:
            r2 = requests.get(
                "https://efts.sec.gov/LATEST/search-index",
                headers={"User-Agent": "deal-flow-tool contact@test.com"},
                params={"q": "Illinois", "dateRange": "custom",
                        "startdt": "2025-09-01", "forms": "D"},
                timeout=12,
            )
            st.write(f"Status: {r2.status_code}")
            if r2.ok:
                hits = r2.json().get("hits", {}).get("hits", [])
                total = r2.json().get("hits", {}).get("total", {})
                st.write(f"Total: {total} | Returned: {len(hits)}")
                if hits:
                    st.write("Keys:", list(hits[0].get("_source", {}).keys()))
                    st.write("Sample:", hits[0].get("_source", {}))
        except Exception as e:
            st.write(f"Error: {e}")

        # 4. Show raw Crunchbase RSS titles to confirm name extraction issue
        st.markdown("---")
        st.markdown("**Crunchbase RSS titles (raw):**")
        try:
            r3 = requests.get("https://news.crunchbase.com/feed/",
                              headers=HEADERS, timeout=8)
            if r3.ok:
                root = ET.fromstring(r3.content)
                for item in root.findall(".//item")[:5]:
                    st.write(f"• {item.findtext('title', '')[:90]}")
        except Exception as e:
            st.write(f"Error: {e}")
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
    <p style="color:#5A5650; font-size:.68rem; line-height:1.7">
    Built by <strong style="color:#9A9490">Catherine Walker </strong><br>
    Tracking pre-seed & seed deals in Fintech, Health, and B2B SaaS<br>
    focusing on Chicago-area Funds.
    </p>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------ #
#  Main Content -- header                                            #
# ------------------------------------------------------------------ #
st.markdown("## The C-Note - {industry}".format(industry=selected_label))
st.markdown('<div class="section-header"> The who, the how, the why — today’s market pulse in under 5 minutes </div>', unsafe_allow_html=True)

if not run_btn:
    st.markdown("""
    <div style="border:1px solid #2A2A30; border-left:3px solid #C9A84C; 
    background:#1C1C20; padding:28px 32px; border-radius:2px; margin-bottom:2rem">
    <p style="color:#C9A84C; font-size:.65rem; font-weight:700; 
    letter-spacing:.16em; text-transform:uppercase; margin:0 0 12px 0">
    Why This Exists</p>
    <p style="color:#F5F0E8; font-size:1.05rem; line-height:1.8; margin:0">
    Early startup signals appear across fragmented sources long before companies show up in traditional deal databases.
This platform aggregates signals like SEC Form D filings, Show HN launches, and founder RSS feeds to surface potential deals earlier in the sourcing pipeline.
    </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="border:1px solid #2A2A30; background:#1C1C20; 
        padding:20px 24px; border-radius:2px; text-align:center">
        <p style="color:#C9A84C; font-size:1.6rem; font-weight:600; 
        font-family:'Cormorant Garamond',serif; margin:0">6</p>
        <p style="color:#9A9490; font-size:.65rem; font-weight:700; 
        letter-spacing:.14em; text-transform:uppercase; margin:4px 0 0 0">
        Data Sources</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="border:1px solid #2A2A30; background:#1C1C20; 
        padding:20px 24px; border-radius:2px; text-align:center">
        <p style="color:#C9A84C; font-size:1.6rem; font-weight:600; 
        font-family:'Cormorant Garamond',serif; margin:0">4</p>
        <p style="color:#9A9490; font-size:.65rem; font-weight:700; 
        letter-spacing:.14em; text-transform:uppercase; margin:4px 0 0 0">
        Chicago VC Portfolios Tracked</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="border:1px solid #2A2A30; background:#1C1C20; 
        padding:20px 24px; border-radius:2px; text-align:center">
        <p style="color:#C9A84C; font-size:1.6rem; font-weight:600; 
        font-family:'Cormorant Garamond',serif; margin:0">30min</p>
        <p style="color:#9A9490; font-size:.65rem; font-weight:700; 
        letter-spacing:.14em; text-transform:uppercase; margin:4px 0 0 0">
        Cache — Instant on Demo</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#5A5650; font-size:.78rem; line-height:1.7">
    <strong style="color:#9A9490">Sources:</strong> SEC EDGAR Form D · 
    Hacker News Show HN · TechCrunch Funding · Crunchbase News · 
    Built In Chicago · Chicago Inno · NewsAPI · Product Hunt<br>
    <strong style="color:#9A9490">Portfolios:</strong> Chicago Ventures · 
    Hyde Park Angels · M25 · Origin Ventures
    </p>
    """, unsafe_allow_html=True)
    st.stop()

# ── Run pipeline with progress indicator ── #
@st.cache_data(ttl=1800, show_spinner=False)
def run_pipeline(industry_key: str, scraper_name: str):
    st.cache_data.clear()  # ← add this, remove after one run
    
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
<p style="color:#5A5650; font-size:.75rem; margin:-8px 0 16px 0">
Ranked by composite score: funding stage · thesis alignment ·
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
 
    source_line = f'<p style="color:#5A5650;font-size:.72rem;margin-top:6px;">Source: {source}</p>' if source else ""
 
    st.markdown(f"""
    <div class="pick-card">
      <h4>#{i+1} {name_html} &nbsp; {badges}</h4>
      <p>{rationale}</p>
      <p style="color:#8A96A8;font-size:.78rem;margin-top:4px;">Score: <b>{score}</b></p>
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
<p style="color:#5A5650; font-size:.75rem; margin:-8px 0 16px 0">
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