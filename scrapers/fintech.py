from scrapers.base import BaseScraper
from scrapers.api_clients import (
    hn_show_stories, edgar_form_d_batch, parse_rss_batch,
    newsapi_search, producthunt_launches, crunchbase_recent_funding, fetch_funding_rss
)
from typing import List, Dict

FINTECH_RSS = [
    ("https://www.pymnts.com/feed/",                     "PYMNTS"),
    ("https://www.fintechfutures.com/feed/",             "Fintech Futures"),
    ("https://www.finsmes.com/feed",                     "FinSMEs Funding"),
    ("https://techcrunch.com/tag/fintech/feed/",         "TechCrunch Fintech"),
    ("https://news.crunchbase.com/feed/",                "Crunchbase News"),
]

# Expanded from 5 → 25 terms covering every fintech niche
FINTECH_EDGAR_TERMS = [
    "fintech", "payments", "neobank", "insurtech", "wealthtech",
    "regtech", "lendtech", "proptech", "paytech", "banktech",
    "digital banking", "open banking", "embedded finance", "crypto",
    "defi", "blockchain payments", "b2b payments", "cross-border",
    "remittance", "credit scoring", "buy now pay later", "bnpl",
    "robo-advisor", "invoice financing", "treasury management",
]

FINTECH_HN_KEYWORDS = [
    "fintech", "payment", "banking", "neobank", "stripe", "plaid",
    "lending", "insurance", "crypto", "defi", "embedded finance",
    "treasury", "invoice", "payroll", "remittance",
]

FINTECH_PH_KEYWORDS = [
    "finance", "payments", "banking", "investing", "crypto", "insurance",
]


class FintechScraper(BaseScraper):
    sector = "Fintech"
    source_name = "Fintech Scraper"

    def fetch_items(self) -> List[Dict]:
        items = []

        # 1. Funding-specific RSS
        items.extend(parse_rss_batch(FINTECH_RSS))

        # 2. Global funding RSS (Crunchbase News, TechCrunch Funding etc.)
        items.extend(fetch_funding_rss())

        # 3. EDGAR Form D — 25 terms, 60-day window
        items.extend(edgar_form_d_batch(FINTECH_EDGAR_TERMS, days_back=30))

        # 4. HN Show HN
        for story in hn_show_stories(limit=100):
            if any(kw in story["description"].lower() for kw in FINTECH_HN_KEYWORDS):
                items.append(story)

        # 5. Crunchbase (if key set)
        items.extend(crunchbase_recent_funding(days_back=30))

        # 6. Product Hunt (if token set)
        for launch in producthunt_launches(days_back=14):
            desc = launch.get("description", "").lower()
            if any(kw in desc for kw in FINTECH_PH_KEYWORDS):
                items.append(launch)

        # 7. NewsAPI
        items.extend(newsapi_search("fintech startup seed funding raised series"))
        items.extend(newsapi_search("payments startup pre-seed angel round"))

        return items


def scrape_fintech():
    return FintechScraper().run()