from scrapers.base import BaseScraper
from scrapers.api_clients import (
    hn_show_stories, edgar_form_d_batch, parse_rss_batch,
    newsapi_search, producthunt_launches, crunchbase_recent_funding, fetch_funding_rss
)
from typing import List, Dict

RETAIL_RSS = [
    ("https://www.retaildive.com/feeds/news/",               "Retail Dive"),
    ("https://www.pymnts.com/category/commerce/feed/",       "PYMNTS Commerce"),
    ("https://techcrunch.com/tag/e-commerce/feed/",          "TechCrunch Ecommerce"),
    ("https://news.crunchbase.com/feed/",                    "Crunchbase News"),
]

# Expanded — covers DTC, resale, social commerce, sustainability, food/bev
RETAIL_EDGAR_TERMS = [
    "ecommerce", "retail", "fashion", "consumer", "marketplace",
    "direct to consumer", "dtc", "subscription box", "resale",
    "recommerce", "social commerce", "live shopping", "pop-up",
    "food delivery", "meal kit", "grocery tech", "beverage",
    "beauty tech", "personal care", "pet care", "home goods",
    "sustainable fashion", "circular fashion", "rental fashion",
    "luxury resale", "sneakers", "streetwear",
]

RETAIL_HN_KEYWORDS = [
    "ecommerce", "shop", "retail", "fashion", "marketplace", "consumer",
    "brand", "store", "dtc", "subscription", "resale", "recommerce",
    "social commerce", "checkout", "cart", "dropship",
]

RETAIL_PH_KEYWORDS = [
    "shop", "store", "ecommerce", "fashion", "marketplace", "consumer",
    "brand", "retail", "subscription", "product",
]


class ConsumerRetailScraper(BaseScraper):
    sector = "Consumer Retail / Fashion / Ecommerce"
    source_name = "Consumer Retail Scraper"

    def fetch_items(self) -> List[Dict]:
        items = []
        items.extend(parse_rss_batch(RETAIL_RSS))
        items.extend(fetch_funding_rss())
        items.extend(edgar_form_d_batch(RETAIL_EDGAR_TERMS, days_back=30))
        for story in hn_show_stories(limit=100):
            if any(kw in story["description"].lower() for kw in RETAIL_HN_KEYWORDS):
                items.append(story)
        items.extend(crunchbase_recent_funding(days_back=30))
        for launch in producthunt_launches(days_back=14):
            desc = launch.get("description", "").lower()
            if any(kw in desc for kw in RETAIL_PH_KEYWORDS):
                items.append(launch)
        items.extend(newsapi_search("ecommerce startup seed funding raises DTC"))
        items.extend(newsapi_search("consumer brand startup pre-seed angel round"))
        return items


def scrape_consumer_retail():
    return ConsumerRetailScraper().run()