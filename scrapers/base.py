"""
Base scraper — API/feed based, Streamlit Cloud safe.
No HTML scraping. All sources return JSON or RSS XML.

Filtering philosophy:
  - SEC EDGAR Form D items always pass  (legally filed fundraises — ground truth)
  - HN Show HN items always pass        (founders self-announcing products)
  - RSS / NewsAPI items MUST contain a  funding signal keyword to pass
    (filters out news articles about Target, Amazon, etc.)
  - All items are then checked against the established-company blocklist
    and the article-headline detector in utils.text
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
import pandas as pd

from utils.text import (
    extract_company_name,
    is_valid_company_name,
    normalize_name,
    has_funding_signal,
)

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 10

# Sources that are inherently deal-flow (no funding-signal gate needed)
TRUSTED_SOURCES = {
    "sec edgar form d",
    "hacker news (show hn)",
    "hacker news",
}


class BaseScraper(ABC):
    sector: str = "Unknown"
    source_name: str = "Unknown"

    def __init__(self):
        self._seen_normalized: set = set()

    @abstractmethod
    def fetch_items(self) -> List[Dict]:
        """Return a list of raw dicts with at minimum 'name' and 'description'."""
        ...

    def _get(self, url: str, params: dict = None) -> Optional[requests.Response]:
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
            if r.ok:
                return r
        except Exception as e:
            logger.debug(f"Request failed: {url} — {e}")
        return None

    def _normalize_row(self, row: Dict) -> Optional[Dict]:
        source = row.get("source", self.source_name).lower()

        # For RSS / NewsAPI sources, require a funding signal in the full text
        # before even attempting name extraction.
        if not any(trusted in source for trusted in TRUSTED_SOURCES):
            full_text = f"{row.get('name', '')} {row.get('description', '')}"
            if not has_funding_signal(full_text):
                return None  # Skip — article about an established company, not a startup

        raw = row.get("name", "") or row.get("description", "")
        name = extract_company_name(raw)

        if not is_valid_company_name(name):
            return None

        norm = normalize_name(name)
        if norm in self._seen_normalized:
            return None
        self._seen_normalized.add(norm)

        return {
            "name": name,
            "description": row.get("description", name),
            "source": row.get("source", self.source_name),
            "sector": self.sector,
            "url": row.get("url", ""),
        }

    def run(self) -> pd.DataFrame:
        items = self.fetch_items()
        cleaned = [self._normalize_row(r) for r in items]
        cleaned = [r for r in cleaned if r is not None]
        if not cleaned:
            return pd.DataFrame(columns=["name", "description", "source", "sector", "url"])
        return pd.DataFrame(cleaned)