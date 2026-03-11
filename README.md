# 📡 What's New — VC Deal Flow Intelligence

A real-time market analysis tool for identifying early-stage investment opportunities, built to support deal sourcing at Chicago-area VC funds.

---

## Features

- **Multi-industry scraping** across Fintech, Healthcare, Consumer/Retail, Operations/Logistics, Marketing/Social, and Tech (BetaList + Product Hunt)
- **Async concurrent fetching** — all URLs fetched in parallel, 5–10× faster than sequential
- **Retry + backoff** — 3 attempts with exponential wait on network failures
- **Rotating user agents** — reduces blocking from anti-bot measures
- **Company name extraction** — strips nav/footer noise; validated against a blocklist
- **Funding stage detection** — regex-based classifier across Pre-Seed through Series C+
- **Trend labeling** — 10 theme categories (AI/ML, Embedded Finance, Climate, Web3, etc.)
- **Scoring** — composite score from stage, trend signals, and portfolio overlap
- **Human-readable rationale** — one-line summary per company ("Seed stage · trending in AI/ML · overlaps with Brex")
- **Portfolio overlap** — semantic similarity against Chicago Ventures portfolio
- **Competitor radar** — predicts which VC is most likely to invest next
- **Weekly diff** — surfaces what's new since the last run (new companies, stage changes)
- **Export** — CSV download and a styled PDF deal memo
- **Caching** — portfolio data cached 1hr, pipeline results cached 30min for instant demos

---

## Project Structure

```
whatsnew/
├── app.py                    # Streamlit UI
├── requirements.txt
├── snapshots/                # Auto-created; stores per-run JSON snapshots
├── scrapers/
│   ├── base.py               # BaseScraper (async, retry, validation)
│   ├── fintech.py
│   ├── healthcare.py
│   ├── consumer_retail.py
│   ├── operations_logistics.py
│   ├── marketing_social.py
│   └── tech.py               # BetaList + Product Hunt
└── utils/
    ├── text.py               # extract_company_name, is_valid_company_name, BLOCKLIST
    ├── scoring.py            # detect_funding_stage, label_trends, score_company, generate_rationale
    ├── snapshot.py           # save_snapshot, compute_diff
    ├── export.py             # export_csv, export_pdf
    ├── viz.py                # Plotly chart builders
    ├── utils.py              # (original) semantic_overlap, competitor_overlap, market_map, etc.
    └── portfolios.py         # (original) portfolio scrapers
```

---

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| `BaseScraper` abstract class | Eliminates 200+ lines of duplicated code across scrapers |
| `httpx` + `asyncio` | Concurrent fetching; sequential `requests` was the main bottleneck |
| `tenacity` retry decorator | Graceful handling of transient network failures |
| `is_valid_company_name` + BLOCKLIST | Scraping `<h2>/<a>` tags picks up nav/footer noise; this filters it |
| Boolean `is_portfolio` column | Original code produced a sparse NaN column — this is correct |
| `competitor_overlap` called once | Was called twice in original (copy-paste bug) |
| Snapshot + diff | VCs care about velocity; showing what changed since last run is high-signal |
| `@st.cache_data` on pipeline | Critical for live demos — results load instantly after first run |
| PDF memo export | Shareable artifact; shows you think about how analysts actually work |

---

## Adding a New Industry

1. Create `scrapers/my_industry.py` extending `BaseScraper`
2. Set `sector`, `source_name`, and `urls`
3. Implement `parse(self, html, url) -> List[Dict]`
4. Add a `scrape_my_industry()` convenience function
5. Register it in `app.py`'s `INDUSTRIES` dict and `scraper_map`

```python
class MyIndustryScraper(BaseScraper):
    sector = "My Industry"
    source_name = "My Industry Scraper"
    urls = ["https://example.com/startups"]

    def parse(self, html: str, url: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        return [
            {"name": el.get_text(strip=True), "description": el.get_text(strip=True), "url": url}
            for el in soup.find_all("h2")
        ]
```
