from scrapers.base import BaseScraper
from scrapers.api_clients import (
    hn_show_stories, edgar_form_d_batch, parse_rss_batch,
    newsapi_search, producthunt_launches, crunchbase_recent_funding, fetch_funding_rss
)
from typing import List, Dict

LOGISTICS_RSS = [
    ("https://www.supplychaindive.com/feeds/news/",      "Supply Chain Dive"),
    ("https://www.freightwaves.com/news/feed",           "FreightWaves"),
    ("https://techcrunch.com/tag/logistics/feed/",       "TechCrunch Logistics"),
    ("https://news.crunchbase.com/feed/",                "Crunchbase News"),
]

LOGISTICS_EDGAR_TERMS = [
    "logistics", "supply chain", "fulfillment", "freight", "warehouse",
    "last mile", "last-mile", "reverse logistics", "returns",
    "cold chain", "fleet management", "route optimization",
    "shipping tech", "freight brokerage", "drayage", "intermodal",
    "customs", "trade compliance", "procurement tech", "inventory",
    "3pl", "fourth party logistics", "dark store", "micro-fulfillment",
    "autonomous delivery", "drone delivery",
]

LOGISTICS_HN_KEYWORDS = [
    "logistics", "supply chain", "shipping", "freight", "warehouse",
    "delivery", "fleet", "fulfillment", "inventory", "procurement",
    "last mile", "autonomous delivery",
]

LOGISTICS_PH_KEYWORDS = [
    "logistics", "shipping", "delivery", "warehouse", "supply chain",
    "fleet", "freight", "inventory",
]


class OperationsLogisticsScraper(BaseScraper):
    sector = "Operations / Logistics"
    source_name = "Operations Scraper"

    def fetch_items(self) -> List[Dict]:
        items = []
        items.extend(parse_rss_batch(LOGISTICS_RSS))
        items.extend(fetch_funding_rss())
        items.extend(edgar_form_d_batch(LOGISTICS_EDGAR_TERMS, days_back=60))
        for story in hn_show_stories(limit=100):
            if any(kw in story["description"].lower() for kw in LOGISTICS_HN_KEYWORDS):
                items.append(story)
        items.extend(crunchbase_recent_funding(days_back=30))
        for launch in producthunt_launches(days_back=14):
            desc = launch.get("description", "").lower()
            if any(kw in desc for kw in LOGISTICS_PH_KEYWORDS):
                items.append(launch)
        items.extend(newsapi_search("logistics startup seed funding raises"))
        items.extend(newsapi_search("supply chain tech startup pre-seed angel"))
        return items


def scrape_operations_logistics():
    return OperationsLogisticsScraper().run()