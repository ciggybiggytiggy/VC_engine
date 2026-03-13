from scrapers.base import BaseScraper
from scrapers.api_clients import (
    hn_show_stories, edgar_form_d_batch, parse_rss_batch,
    newsapi_search, producthunt_launches, crunchbase_recent_funding, fetch_funding_rss
)
from typing import List, Dict

HEALTHCARE_RSS = [
    ("https://medcitynews.com/feed/",                    "MedCity News"),
    ("https://www.healthcareitnews.com/rss.xml",         "Healthcare IT News"),
    ("https://www.statnews.com/feed/",                   "STAT News"),
    ("https://hitconsultant.net/feed/",                  "HIT Consultant"),
    ("https://techcrunch.com/tag/health/feed/",          "TechCrunch Health"),
    ("https://www.fiercehealthcare.com/rss/xml",         "Fierce Healthcare"),
]

HEALTHCARE_EDGAR_TERMS = [
    "health", "biotech", "medtech", "telehealth", "pharma",
    "digital health", "clinical", "therapeutics", "diagnostics",
    "wearable health", "mental health", "behavioral health",
    "home health", "care coordination", "population health",
    "medical device", "surgical", "genomics", "longevity",
    "women's health", "pediatric health", "oncology", "neurology",
    "health insurance", "pharmacy", "drug discovery",
]

HEALTHCARE_HN_KEYWORDS = [
    "health", "medical", "biotech", "hospital", "clinical", "pharma",
    "drug", "patient", "telehealth", "genomics", "mental health",
    "diagnostic", "wearable", "ehr", "electronic health",
]

HEALTHCARE_PH_KEYWORDS = [
    "health", "medical", "fitness", "wellness", "mental", "therapy",
    "doctor", "patient", "clinical", "biotech",
]


class HealthcareScraper(BaseScraper):
    sector = "Healthcare"
    source_name = "Healthcare Scraper"

    def fetch_items(self) -> List[Dict]:
        items = []
        items.extend(parse_rss_batch(HEALTHCARE_RSS))
        items.extend(fetch_funding_rss())
        items.extend(edgar_form_d_batch(HEALTHCARE_EDGAR_TERMS, days_back=30))
        for story in hn_show_stories(limit=100):
            if any(kw in story["description"].lower() for kw in HEALTHCARE_HN_KEYWORDS):
                items.append(story)
        items.extend(crunchbase_recent_funding(days_back=30))
        for launch in producthunt_launches(days_back=14):
            desc = launch.get("description", "").lower()
            if any(kw in desc for kw in HEALTHCARE_PH_KEYWORDS):
                items.append(launch)
        items.extend(newsapi_search("healthcare startup seed funding biotech raises"))
        items.extend(newsapi_search("digital health medtech pre-seed angel round"))
        return items


def scrape_healthcare():
    return HealthcareScraper().run()