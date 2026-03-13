from typing import List, Dict, Optional

from scrapers.base import BaseScraper
from scrapers.api_clients import (
    edgar_form_d_batch, parse_rss_batch,
    newsapi_search, producthunt_launches, crunchbase_recent_funding,
)

# ── Chicago-only RSS feeds ────────────────────────────────────────── #
# Only feeds that are inherently Chicago-scoped OR geo-tag every item.
# TechCrunch / GeekWire removed — they publish national content with
# no reliable location field, causing non-Chicago companies to slip through.
CHICAGO_RSS = [
    ("https://www.finsmes.com/feed",  "FinSMEs Funding"),  # always "City, State-based" in description
]

# ── EDGAR geographic search terms ────────────────────────────────── #
# EDGAR biz_locations field contains "Chicago, IL" style strings —
# the most reliable Chicago signal in the entire pipeline.
CHICAGO_GEO_TERMS = [
    "Chicago", "Illinois", "Evanston", "Naperville", "Oak Park",
    "Schaumburg", "Downers Grove", "Skokie", "Waukegan", "Joliet",
    "Champaign", "Urbana",
]

CHICAGO_INDUSTRY_TERMS = [
    "fintech Chicago", "healthtech Chicago", "logistics Chicago",
    "proptech Chicago", "foodtech Chicago", "saas Chicago",
    "cleantech Chicago", "edtech Chicago",
]

# ── Source classification ─────────────────────────────────────────── #
EDGAR_SOURCES         = {"sec edgar form d"}
LOCATION_RICH_SOURCES = {"finsmes funding", "finsmes"}

# ── Chicago geo signals — must appear in name/description/url/state ── #
CHICAGO_GEO_SIGNALS = [
    "illinois", "chicago", "evanston", "naperville", "oak park",
    "schaumburg", "downers grove", "lisle", "skokie", "waukegan",
    "joliet", "champaign", "urbana", "peoria", "rockford",
    "chicago, il", "chicago il", ", il ", "(il)",
    "chicago-based", "illinois-based", "chicago startup",
]

# ── Hard-block non-US city names ─────────────────────────────────── #
NON_US_SIGNALS = [
    "berlin", "london", "paris", "amsterdam", "stockholm", "helsinki",
    "vilnius", "warsaw", "munich", "zurich", "singapore", "toronto",
    "sydney", "tokyo", "seoul", "beijing", "shanghai", "dubai",
    "barcelona", "madrid", "milan", "rome", "lisbon", "oslo",
    "copenhagen", "brussels", "vienna", "prague", "budapest",
    "european startup", "uk-based", "uk based",
    # US cities that are NOT Chicago — block to avoid false positives
    # from queries like "Illinois startup" that may return SF/NYC press
    "san francisco", "new york", "los angeles", "boston", "seattle",
    "austin", "miami", "denver", "atlanta", "dallas", "houston",
]


def _has_chicago_signal(text: str) -> bool:
    return any(sig in text for sig in CHICAGO_GEO_SIGNALS)


def _has_non_us_signal(text: str) -> bool:
    return any(sig in text for sig in NON_US_SIGNALS)


def _check_text(row: Dict) -> str:
    """Build the text blob used for geo checks — excludes sector/source."""
    return " ".join([
        str(row.get("name", "")),
        str(row.get("description", "")),
        str(row.get("url", "")),
        str(row.get("state", "")),
        str(row.get("location", "")),
    ]).lower()


class BuiltInChicagoScraper(BaseScraper):
    sector = "Chicago Startup"
    source_name = "Built In Chicago"

    def _normalize_row(self, row: Dict) -> Optional[Dict]:
        source = row.get("source", self.source_name).lower()
        check_text = _check_text(row)

        # Step 1 — hard-block non-Chicago locations regardless of source
        if _has_non_us_signal(check_text):
            return None

        # Step 2 — EDGAR: geo is guaranteed by search terms + biz_locations field.
        # Still require a Chicago signal as a belt-and-suspenders check.
        if any(s in source for s in EDGAR_SOURCES):
            if not _has_chicago_signal(check_text):
                return None
            return super()._normalize_row(row)

        # Step 3 — FinSMEs: always includes "City, State-based" in description.
        # Strict Chicago check required.
        if any(s in source for s in LOCATION_RICH_SOURCES):
            if not _has_chicago_signal(check_text):
                return None
            return super()._normalize_row(row)

        # Step 4 — NewsAPI: queries are already geo-scoped ("Chicago startup...").
        # Require a Chicago signal to catch any query bleed-through.
        if "newsapi" in source:
            if not _has_chicago_signal(check_text):
                return None
            return super()._normalize_row(row)

        # Step 5 — All other sources (Product Hunt, Crunchbase, etc.):
        # No reliable location field — require explicit Chicago signal.
        if not _has_chicago_signal(check_text):
            return None
        return super()._normalize_row(row)

    def fetch_items(self) -> List[Dict]:
        items = []

        # Chicago-scoped RSS only (FinSMEs geo-tags every item)
        items.extend(parse_rss_batch(CHICAGO_RSS))

        # EDGAR — primary Chicago source, real SEC Form D filings
        items.extend(edgar_form_d_batch(CHICAGO_GEO_TERMS, days_back=30))
        items.extend(edgar_form_d_batch(CHICAGO_INDUSTRY_TERMS, days_back=30))

        # NewsAPI — queries explicitly include "Chicago" or "Illinois"
        items.extend(newsapi_search("Chicago startup funding raised seed"))
        items.extend(newsapi_search("Chicago venture capital investment raises"))
        items.extend(newsapi_search("Illinois startup pre-seed angel round"))
        items.extend(newsapi_search("Chicago fintech healthtech raises funding"))

        # Crunchbase — no location filter in API, geo-gated in _normalize_row
        items.extend(crunchbase_recent_funding(days_back=30))

        # Product Hunt — very low Chicago yield, geo-gated in _normalize_row
        items.extend(producthunt_launches(days_back=14, limit=50))

        return items


def scrape_chicago():
    return BuiltInChicagoScraper().run()