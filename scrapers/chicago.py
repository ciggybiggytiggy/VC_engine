from scrapers.base import BaseScraper
from scrapers.api_clients import (
    edgar_form_d_batch, parse_rss_batch,
    newsapi_search, producthunt_launches, crunchbase_recent_funding, fetch_funding_rss
)
from typing import List, Dict

CHICAGO_RSS = [
    ("https://chicagoinno.streetinsider.com/rss",            "Chicago Inno"),
    ("https://www.builtinchicago.org/rss.xml",               "Built In Chicago"),
    ("https://www.geekwire.com/feed/",                       "GeekWire"),
    ("https://news.crunchbase.com/feed/",                    "Crunchbase News"),
    ("https://techcrunch.com/tag/funding/feed/",             "TechCrunch Funding"),
]

# Chicago-area geographic terms — suburbs included
CHICAGO_GEO_TERMS = [
    "Illinois", "Chicago", "Evanston", "Naperville", "Oak Park",
    "Schaumburg", "Rockford", "Peoria", "Champaign", "Urbana",
    "Downers Grove", "Lisle", "Skokie", "Waukegan", "Joliet",
]

# Chicago-area industry strengths
CHICAGO_INDUSTRY_TERMS = [
    "foodtech Chicago", "agtech Illinois", "proptech Chicago",
    "healthtech Chicago", "fintech Chicago", "logistics Chicago",
    "manufacturing tech Illinois", "cleantech Chicago",
    "edtech Chicago", "legaltech Chicago",
]


class BuiltInChicagoScraper(BaseScraper):
    sector = "Chicago Startup"
    source_name = "Built In Chicago"

    def fetch_items(self) -> List[Dict]:
        items = []

        # Local RSS
        items.extend(parse_rss_batch(CHICAGO_RSS))

        # Global funding RSS (catches Chicago companies covered nationally)
        items.extend(fetch_funding_rss())

        # EDGAR — geo terms + industry terms
        items.extend(edgar_form_d_batch(CHICAGO_GEO_TERMS, days_back=60))
        items.extend(edgar_form_d_batch(CHICAGO_INDUSTRY_TERMS, days_back=60))

        # Crunchbase (if key set) — recent early-stage nationally, filter post-hoc
        items.extend(crunchbase_recent_funding(days_back=30))

        # Product Hunt (no geo filter — Chicago founders launch globally)
        items.extend(producthunt_launches(days_back=14, limit=50))

        # NewsAPI — Chicago-specific queries
        items.extend(newsapi_search("Chicago startup funding raised seed"))
        items.extend(newsapi_search("Chicago venture capital investment raises"))
        items.extend(newsapi_search("Illinois startup pre-seed angel round"))

        return items


def scrape_chicago():
    return BuiltInChicagoScraper().run()