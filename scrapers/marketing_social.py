from scrapers.base import BaseScraper
from scrapers.api_clients import (
    hn_show_stories, edgar_form_d_batch, parse_rss_batch,
    newsapi_search, producthunt_launches, crunchbase_recent_funding, fetch_funding_rss
)
from typing import List, Dict

MARKETING_RSS = [
    ("https://www.marketingdive.com/feeds/news/",            "Marketing Dive"),
    ("https://techcrunch.com/tag/social/feed/",              "TechCrunch Social"),
    ("https://news.crunchbase.com/feed/",                    "Crunchbase News"),
]

MARKETING_EDGAR_TERMS = [
    "marketing", "advertising", "social media", "creator", "influencer",
    "martech", "adtech", "content marketing", "performance marketing",
    "affiliate marketing", "programmatic", "connected tv", "ctv",
    "retail media", "out of home", "ooh advertising", "email marketing",
    "sms marketing", "loyalty platform", "referral marketing",
    "brand safety", "identity resolution", "cdp", "customer data platform",
    "attribution", "measurement", "analytics platform",
]

MARKETING_HN_KEYWORDS = [
    "marketing", "social media", "creator", "influencer", "ads",
    "brand", "content", "saas", "martech", "adtech", "newsletter",
    "community", "audience", "growth",
]

MARKETING_PH_KEYWORDS = [
    "marketing", "social", "creator", "content", "analytics",
    "email", "newsletter", "community", "brand", "growth",
]


class MarketingSocialScraper(BaseScraper):
    sector = "Marketing / Social"
    source_name = "Marketing Social Scraper"

    def fetch_items(self) -> List[Dict]:
        items = []
        items.extend(parse_rss_batch(MARKETING_RSS))
        items.extend(fetch_funding_rss())
        items.extend(edgar_form_d_batch(MARKETING_EDGAR_TERMS, days_back=60))
        for story in hn_show_stories(limit=100):
            if any(kw in story["description"].lower() for kw in MARKETING_HN_KEYWORDS):
                items.append(story)
        items.extend(crunchbase_recent_funding(days_back=30))
        for launch in producthunt_launches(days_back=14):
            desc = launch.get("description", "").lower()
            if any(kw in desc for kw in MARKETING_PH_KEYWORDS):
                items.append(launch)
        items.extend(newsapi_search("martech adtech startup seed funding raises"))
        items.extend(newsapi_search("creator economy social media startup pre-seed"))
        return items


def scrape_marketing_social():
    return MarketingSocialScraper().run()