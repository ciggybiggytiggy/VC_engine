from scrapers.base import BaseScraper
from scrapers.api_clients import (
    hn_show_stories, hn_new_stories, edgar_form_d_batch, parse_rss_batch,
    newsapi_search, producthunt_launches, crunchbase_recent_funding, fetch_funding_rss
)
from typing import List, Dict

TECH_RSS = [
    ("https://techcrunch.com/tag/funding/feed/",             "TechCrunch Funding"),
    ("https://techcrunch.com/tag/startups/feed/",            "TechCrunch Startups"),
    ("https://venturebeat.com/category/business/feed/",      "VentureBeat"),
    ("https://thenextweb.com/feed/",                         "The Next Web"),
    ("https://news.crunchbase.com/feed/",                    "Crunchbase News"),
    ("https://www.geekwire.com/feed/",                       "GeekWire"),
    ("https://eu-startups.com/feed/",                        "EU Startups"),
]

TECH_EDGAR_TERMS = [
    "software", "saas", "artificial intelligence", "machine learning",
    "platform", "developer tools", "devtools", "api platform",
    "cloud infrastructure", "data platform", "analytics",
    "cybersecurity", "zero trust", "identity platform",
    "generative ai", "llm", "foundation model", "ai agent",
    "robotics", "automation", "rpa", "no-code", "low-code",
    "iot platform", "edge computing", "quantum computing",
    "space tech", "satellite", "drone tech",
]

SEC_EARLY_TERMS = [
    "pre-seed", "series seed", "series a", "angel round",
    "seed round", "seed stage", "early stage",
]


class BetaListScraper(BaseScraper):
    """Show HN = founders self-announcing — best proxy for BetaList."""
    sector = "Startup"
    source_name = "Hacker News (Show HN)"

    def fetch_items(self) -> List[Dict]:
        return hn_show_stories(limit=100)


class YCScraper(BaseScraper):
    sector = "Tech Product"
    source_name = "Y Combinator / HN"

    def fetch_items(self) -> List[Dict]:
        items = []
        items.extend(hn_new_stories(limit=100))
        items.extend(edgar_form_d_batch(TECH_EDGAR_TERMS, days_back=60))
        items.extend(parse_rss_batch(TECH_RSS))
        items.extend(fetch_funding_rss())
        items.extend(crunchbase_recent_funding(days_back=30))
        items.extend(producthunt_launches(days_back=7, limit=100))
        items.extend(newsapi_search("startup funding raised seed series AI SaaS"))
        items.extend(newsapi_search("tech startup pre-seed angel round raises"))
        return items


class SECFormDScraper(BaseScraper):
    sector = "Startup"
    source_name = "SEC EDGAR Form D"

    def fetch_items(self) -> List[Dict]:
        return edgar_form_d_batch(SEC_EARLY_TERMS, days_back=30)


def scrape_betalist():
    return BetaListScraper().run()

def scrape_producthunt():
    return YCScraper().run()

def scrape_yc():
    return YCScraper().run()

def scrape_sec_form_d():
    return SECFormDScraper().run()