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
from scrapers.tech import scrape_betalist, scrape_producthunt, scrape_yc, scrape_sec_form_d
from scrapers.chicago import scrape_chicago

from utils.scoring import detect_funding_stage, label_trends, score_company, generate_rationale
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
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Figtree:wght@300;400;500;600;700&display=swap');

  /* ── Obsidian & Champagne — VC War Room ── */
  :root {
    --obsidian:    #0C0C0E;
    --carbon:      #141416;
    --graphite:    #1C1C20;
    --panel:       #1E1E22;
    --border:      #2A2A30;
    --border-warm: #3A3520;
    --champagne:   #C9A84C;
    --champagne-lt:#E8C97A;
    --champagne-dk:#8B6E2A;
    --emerald:     #2ECC8F;
    --emerald-lt:  #4DFFA8;
    --ivory:       #F5F0E8;
    --stone:       #9A9490;
    --ash:         #5A5650;
    --white:       #FDFCFA;
  }

  /* ── linen texture background ── */
  [data-testid="stAppViewContainer"] {
    background-color: var(--obsidian);
    background-image:
      repeating-linear-gradient(
        -45deg,
        transparent 0px,
        transparent 2px,
        rgba(201,168,76,0.018) 2px,
        rgba(201,168,76,0.018) 3px
      ),
      repeating-linear-gradient(
        45deg,
        transparent 0px,
        transparent 2px,
        rgba(201,168,76,0.012) 2px,
        rgba(201,168,76,0.012) 3px
      ),
      radial-gradient(ellipse 80% 60% at 15% 10%, rgba(201,168,76,0.04) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 85% 90%, rgba(46,204,143,0.03) 0%, transparent 50%);
    font-family: 'Figtree', sans-serif;
  }

  /* ── main content panel ── */
  [data-testid="stMainBlockContainer"],
  [data-testid="block-container"] {
    background: rgba(20, 20, 22, 0.97) !important;
    border-radius: 2px !important;
    padding: 2.5rem 3rem !important;
    border: 1px solid var(--border) !important;
    border-top: 2px solid var(--champagne-dk) !important;
    box-shadow:
      0 0 0 1px rgba(201,168,76,0.06),
      0 32px 80px rgba(0,0,0,0.6),
      inset 0 1px 0 rgba(201,168,76,0.08) !important;
  }

  /* ── text ── */
  [data-testid="stMainBlockContainer"],
  [data-testid="stMainBlockContainer"] p,
  [data-testid="stMainBlockContainer"] span,
  [data-testid="stMainBlockContainer"] div,
  [data-testid="stMainBlockContainer"] label,
  [data-testid="stMainBlockContainer"] li {
    color: var(--ivory) !important;
    font-family: 'Figtree', sans-serif !important;
  }

  /* ── headings ── */
  h1 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 600 !important;
    font-size: 2.6rem !important;
    letter-spacing: 0.01em !important;
    color: var(--champagne-lt) !important;
    line-height: 1.1 !important;
  }
  h2, h3 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 600 !important;
    color: var(--ivory) !important;
    letter-spacing: 0.02em !important;
  }
  h4 {
    font-family: 'Figtree', sans-serif !important;
    font-weight: 600 !important;
    color: var(--ivory) !important;
  }

  /* ── sidebar ── */
  [data-testid="stSidebar"] {
    background: var(--carbon) !important;
    border-right: 1px solid var(--border) !important;
    border-right-color: var(--border-warm) !important;
  }
  [data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--champagne-dk), var(--champagne), var(--champagne-dk));
  }
  [data-testid="stSidebar"] *,
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] div {
    color: var(--stone) !important;
    font-family: 'Figtree', sans-serif !important;
  }
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3,
  [data-testid="stSidebar"] label {
    color: var(--champagne) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
  }
  [data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--champagne) !important;
    border: 1px solid var(--champagne-dk) !important;
    font-weight: 600 !important;
    border-radius: 2px !important;
    font-family: 'Figtree', sans-serif !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-size: 0.72rem !important;
    transition: all 0.2s ease !important;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: var(--champagne) !important;
    color: var(--obsidian) !important;
    border-color: var(--champagne) !important;
    box-shadow: 0 0 20px rgba(201,168,76,0.25) !important;
  }

  /* ── metric cards ── */
  [data-testid="metric-container"] {
    background: var(--graphite) !important;
    border: 1px solid var(--border) !important;
    border-bottom: 2px solid var(--champagne-dk) !important;
    border-radius: 2px !important;
    padding: 20px 24px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    position: relative !important;
  }
  [data-testid="metric-container"] label {
    color: var(--ash) !important;
    font-size: 0.65rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    font-family: 'Figtree', sans-serif !important;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--champagne-lt) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2.4rem !important;
    font-weight: 600 !important;
    line-height: 1 !important;
  }

  /* ── section headers ── */
  .section-header {
    font-family: 'Figtree', sans-serif !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    color: var(--champagne) !important;
    padding: 0 0 12px 0 !important;
    border-bottom: 1px solid var(--border-warm) !important;
    margin-bottom: 20px !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
  }

  /* ── top-pick cards ── */
  .pick-card {
    background: var(--graphite);
    border: 1px solid var(--border);
    border-left: 3px solid var(--champagne-dk);
    border-radius: 2px;
    padding: 20px 24px;
    margin-bottom: 10px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.25);
    transition: all 0.25s ease;
    position: relative;
  }
  .pick-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 40px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--champagne-dk));
    border-radius: 0;
  }
  .pick-card:hover {
    border-left-color: var(--champagne);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 1px rgba(201,168,76,0.15);
    transform: translateX(3px);
  }
  .pick-card h4 {
    margin: 0 0 6px 0 !important;
    color: var(--ivory) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
  }
  .pick-card h4 a {
    color: var(--champagne-lt) !important;
    text-decoration: none !important;
    border-bottom: 1px solid rgba(201,168,76,0.25) !important;
  }
  .pick-card h4 a:hover {
    color: var(--white) !important;
    border-bottom-color: var(--champagne) !important;
  }
  .pick-card p {
    margin: 4px 0 0 0 !important;
    color: var(--stone) !important;
    font-size: .83rem !important;
    line-height: 1.65 !important;
    font-family: 'Figtree', sans-serif !important;
  }

  /* ── badges ── */
  .badge {
    display: inline-block;
    background: transparent;
    color: var(--champagne) !important;
    border-radius: 1px;
    padding: 2px 8px;
    font-size: .60rem;
    font-weight: 700;
    margin-right: 6px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border: 1px solid var(--champagne-dk);
    font-family: 'Figtree', sans-serif !important;
  }
  .badge-green {
    background: transparent !important;
    color: var(--emerald) !important;
    border: 1px solid rgba(46,204,143,0.4) !important;
  }
  .badge-orange {
    background: transparent !important;
    color: var(--champagne-lt) !important;
    border: 1px solid rgba(201,168,76,0.5) !important;
  }

  /* ── new-tag diff pill ── */
  .new-tag {
    background: transparent;
    color: var(--emerald) !important;
    border-radius: 1px;
    padding: 2px 8px;
    font-size: .60rem;
    font-weight: 700;
    margin-left: 6px;
    border: 1px solid rgba(46,204,143,0.4);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'Figtree', sans-serif !important;
  }

  /* ── dataframes ── */
  [data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    overflow: hidden !important;
  }

  /* ── expanders ── */
  [data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
    background: var(--graphite) !important;
  }

  /* ── horizontal rule ── */
  hr {
    border: none !important;
    border-top: 1px solid var(--border-warm) !important;
    margin: 2rem 0 !important;
  }

  /* ── info / warning / success boxes ── */
  [data-testid="stAlert"] {
    background: var(--graphite) !important;
    border: 1px solid var(--border-warm) !important;
    border-left: 3px solid var(--champagne-dk) !important;
    border-radius: 2px !important;
    color: var(--ivory) !important;
  }

  /* ── status widget ── */
  [data-testid="stStatusWidget"] {
    background: var(--graphite) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
  }

  /* ── selectbox / multiselect ── */
  [data-testid="stSelectbox"] > div,
  [data-testid="stMultiSelect"] > div {
    background: var(--graphite) !important;
    border-color: var(--border) !important;
    border-radius: 2px !important;
    color: var(--ivory) !important;
  }

  /* ── text inputs ── */
  [data-testid="stTextInput"] input {
    background: var(--graphite) !important;
    border-color: var(--border) !important;
    border-radius: 2px !important;
    color: var(--ivory) !important;
    font-family: 'Figtree', sans-serif !important;
  }
  [data-testid="stTextInput"] input:focus {
    border-color: var(--champagne-dk) !important;
    box-shadow: 0 0 0 1px rgba(201,168,76,0.2) !important;
  }

  /* ── scrollbar ── */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: var(--carbon); }
  ::-webkit-scrollbar-thumb {
    background: var(--border-warm);
    border-radius: 0;
  }
  ::-webkit-scrollbar-thumb:hover { background: var(--champagne-dk); }
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
        "tech_betalist": scrape_betalist,
        "tech_yc": scrape_yc,
        "tech_sec": scrape_sec_form_d,
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
        "tech_betalist": ("Tech — BetaList", "tech_betalist"),
        "tech_yc": ("Tech — Y Combinator", "tech_yc"),
        "healthcare": ("Healthcare", "healthcare"),
        "consumer_retail_fashion": ("CPG", "consumer_retail_fashion"),
        "operations_logistics": ("Operations / Logistics", "operations_logistics"),
        "marketing_social": ("Marketing / Social", "marketing_social"),
        "chicago": ("Chicago Startups", "chicago"),
    }

    selected_label = st.selectbox(
        "Industry",
        options=[v[0] for v in INDUSTRIES.values()],
    )
    selected_key = [k for k, v in INDUSTRIES.items() if v[0] == selected_label][0]
    selected_scraper = INDUSTRIES[selected_key][1]

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

# ------------------------------------------------------------------ #
#  Main content                                                        #
# ------------------------------------------------------------------ #
st.markdown('<div class="section-header"> The who, the how, the why — today’s market pulse in under 5 minutes </div>', unsafe_allow_html=True)

if not run_btn:
    st.info("Select an industry in the sidebar and click **Run Analysis** to get started.")
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
    n_new = len(diff["new_companies"])
    n_stage = len(diff["stage_changes"])
    prev_date = diff["previous_date"]
    st.success(
        f"**Since {prev_date}:** {n_new} new companies detected · "
        f"{n_stage} stage changes"
    )

    with st.expander(f"🆕 {n_new} New Companies Since Last Run", expanded=n_new > 0):
        if not diff["new_companies"].empty:
            cols_to_show = ["name", "funding_stage", "trend", "rationale", "score"]
            available = [c for c in cols_to_show if c in diff["new_companies"].columns]
            st.dataframe(diff["new_companies"][available], use_container_width=True)
        else:
            st.write("No new companies detected.")

    if not diff["stage_changes"].empty:
        with st.expander(f"📈 {n_stage} Stage Changes"):
            st.dataframe(diff["stage_changes"], use_container_width=True)

# ------------------------------------------------------------------ #
#  KPI metrics row                                                     #
# ------------------------------------------------------------------ #
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Companies", len(df))
m2.metric("Seed or Earlier", len(df[df["funding_stage"].isin(["Pre-Seed", "Seed"])]))
m3.metric("With Trend Signal", len(df[df["trend"] != ""]))
m4.metric("Portfolio Matches", len(df[df["is_portfolio"]]))
m5.metric("Avg Score", f"{df['score'].mean():.1f}" if "score" in df.columns else "—")

st.markdown("---")

# ------------------------------------------------------------------ #
#  Top 5 Picks                                                         #
# ------------------------------------------------------------------ #
st.markdown('<div class="section-header"> Catherine\'s Top 5 of The Week </div>', unsafe_allow_html=True)

top5 = df_filtered.nlargest(5, "score").reset_index(drop=True) if "score" in df_filtered.columns else df_filtered.head(5)

for i, row in top5.iterrows():
    stage = row.get("funding_stage", "")
    trend = row.get("trend", "")
    rationale = row.get("rationale", "")
    score = row.get("score", "")
    name = row.get("name", "Unknown")
    url = row.get("url", "")

    stage_class = "badge-green" if stage in ("Pre-Seed", "Seed") else "badge-orange" if stage == "Series A" else "badge"
    name_html = f'<a href="{url}" target="_blank">{name}</a>' if url else name

    badges = f'<span class="badge {stage_class}">{stage}</span>'
    if trend:
        for t in trend.split(",")[:2]:
            badges += f'<span class="badge">{t.strip()}</span>'

    st.markdown(f"""
    <div class="pick-card">
      <h4>#{i+1} {name_html} &nbsp; {badges}</h4>
      <p>{rationale}</p>
      <p style="color:#8A96A8;font-size:.78rem;margin-top:4px;">Score: <b>{score}</b></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

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
st.markdown('<div class="section-header"> Deal Flow Radar</div>', unsafe_allow_html=True)

df_radar = df_filtered.nlargest(8, "deal_flow_score")[[
    "name", "funding_stage", "trend", "predicted_investor", "deal_flow_score", "rationale"
]].reset_index(drop=True)
df_radar.insert(0, "Rank", range(1, len(df_radar) + 1))

col_tbl, col_chart = st.columns([1, 1])
with col_tbl:
    st.dataframe(df_radar[["Rank", "name", "funding_stage", "predicted_investor", "deal_flow_score"]], use_container_width=True)
with col_chart:
    st.plotly_chart(make_deal_flow_bar(df_radar.rename(columns={"deal_flow_score": "deal_flow_score"})), use_container_width=True, key="deal_flow_bar")

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
    show_cols = ["name", "funding_stage", "trend", "rationale", "score"]
    st.dataframe(df_seed[[c for c in show_cols if c in df_seed.columns]].reset_index(drop=True), use_container_width=True)

with col_trend:
    st.markdown('<div class="section-header"> Trending Now</div>', unsafe_allow_html=True)
    df_trending = df_filtered[(df_filtered["trend"] != "") & (df_filtered["trend"].notna())].head(8)
    st.dataframe(df_trending[[c for c in show_cols if c in df_trending.columns]].reset_index(drop=True), use_container_width=True)

# ------------------------------------------------------------------ #
#  Portfolio Overlap                                                   #
# ------------------------------------------------------------------ #
st.markdown('<div class="section-header"> Highest Portfolio Overlap</div>', unsafe_allow_html=True)
overlap_cols = ["name", "funding_stage", "trend", "portfolio_overlap_score", "closest_portfolio_company", "competitor_overlap_score", "rationale"]
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