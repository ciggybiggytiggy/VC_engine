"""
Portfolio data for Chicago Ventures and competitor VCs.

Chicago Ventures portfolio is hardcoded from chicagoventures.com/companies
(last updated March 2026) — avoids brittle JS-rendered HTML scraping.

Competitor portfolios still attempt live scraping but fall back to
empty dict gracefully if blocked.
"""

from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from typing import Dict

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# ── Chicago Ventures — hardcoded from chicagoventures.com/companies ── #
# Format: "Company Name": "description for semantic matching"

CHICAGO_VENTURES_PORTFOLIO: Dict[str, str] = {
    # Fintech
    "AeroPay":      "contactless digital bank-to-bank payments open banking A2A",
    "BlueTape":     "payment financing construction industry buy now pay later building materials",
    "FranShares":   "alternative investing platform franchises passive income portfolio diversification",

    # Healthcare
    "Andros":       "provider data digitally transform provider network management healthcare",
    "Annie":        "AI-powered assistant automates workflows dental practices revenue capture",
    "Datica":       "healthcare cloud compliance HIPAA data integration",
    "Dina":         "AI care coordination hospitals health plans in-home providers",

    # Supply Chain / Logistics
    "CognitOps":    "AI warehouse management software supply chain automation",
    "Forager":      "freight logistics supply chain acquired Arrive Logistics",
    "GoodShip":     "freight orchestration procurement platform all-in-one logistics",
    "OneRail":      "fulfillment orchestration last-mile delivery logistics",

    # Enterprise Tools / SaaS
    "Catalytic":    "workflow automation enterprise tools acquired PagerDuty",
    "Compliant":    "AI data compliance risk management digital media supply chain",
    "GAN Integrity":"compliance software policies training third parties investigations",
    "Entegrata":    "Azure lakehouse legal industry data management legaltech",

    # Construction / Proptech
    "BuildForce":   "workforce management electrical construction plan grow manage pay",
    "Cartavi":      "real estate document management proptech acquired DocuSign",
    "GreenLite":    "construction permit fast predictable transparent permitting",

    # Commerce / Retail
    "Blitsy":       "craft retail ecommerce marketplace acquired AC Moore",
    "CoPilot":      "personal car shopping expert consumer marketplace mobility",
    "Curbside":     "retail curbside pickup commerce acquired Rakuten",

    # Consumer Media / Entertainment
    "Cameo":        "personalized video shoutouts creator economy consumer media",
    "Gunslinger":   "multiplayer mobile gaming studios",

    # Marketing
    "Bound":        "audience insights website personalization digital marketers",
    "Donde":        "mobile marketing personalization acquired Mobify",
    "G2":           "software marketplace reviews B2B SaaS marketing",

    # Education
    "Betterfly":    "online learning marketplace acquired TakeLessons",
    "Curiosity":    "educational content platform acquired Discovery",
    "GetSet":       "student success growth mindset education",

    # Data Management
    "Data.world":   "collaborative data resource data catalog management",
    "Food Genius":  "food data analytics acquired US Foods",

    # Hospitality
    "Chowly":       "restaurant POS integration third-party online ordering hospitality tech",
}


def get_chicago_ventures_portfolio() -> Dict[str, str]:
    """Return hardcoded Chicago Ventures portfolio. Always succeeds."""
    return CHICAGO_VENTURES_PORTFOLIO.copy()


# ── Competitor portfolio scrapers (best-effort, fail gracefully) ──── #

def _safe_get(url: str, timeout: int = 10) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception:
        return None


def _scrape_generic(url: str) -> Dict[str, str]:
    """Generic portfolio scraper for VC sites."""
    soup = _safe_get(url)
    companies: Dict[str, str] = {}
    if soup is None:
        return companies
    for card in soup.find_all(["div", "li", "article"]):
        name_tag = card.find(["h2", "h3", "h4", "strong", "b"])
        desc_tag = card.find("p")
        if name_tag:
            name = name_tag.get_text(strip=True)
            desc = desc_tag.get_text(strip=True) if desc_tag else ""
            if name and 3 < len(name) < 80:
                companies[name] = desc
    if not companies:
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            if text and 3 < len(text) < 60:
                companies[text] = ""
    return companies


def scrape_chicago_ventures_portfolio() -> Dict[str, str]:
    """Returns hardcoded portfolio — no scraping needed."""
    return get_chicago_ventures_portfolio()


def scrape_hyde_park_portfolio() -> Dict[str, str]:
    return _scrape_generic("https://hydeparkventurepartners.com/portfolio")


def scrape_m25_portfolio() -> Dict[str, str]:
    return _scrape_generic("https://m25.vc/portfolio")


def scrape_origin_ventures() -> Dict[str, str]:
    return _scrape_generic("https://www.originventures.com/portfolio")