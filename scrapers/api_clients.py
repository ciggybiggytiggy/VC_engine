"""
Reusable API clients for all scrapers.

Sources:
1. Hacker News Firebase API      — no key, no rate limit
2. SEC EDGAR full-text search    — no key, US government
3. NewsAPI.org                   — requires NEWSAPI_KEY in Streamlit secrets
4. RSS parser                    — works for any RSS/Atom feed
5. Product Hunt API              — requires PRODUCTHUNT_TOKEN in Streamlit secrets
                                   Get free token at producthunt.com/v2/oauth/applications
6. Crunchbase API                — requires CRUNCHBASE_KEY in Streamlit secrets
                                   Free tier: crunchbase.com/pages/crunchbase-basic-access
"""

import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import requests
import streamlit as st

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 10


# ── Secret helpers ────────────────────────────────────────────────────── #

def _get_secret(key: str) -> Optional[str]:
    try:
        val = st.secrets.get(key)
        if val:
            return val
    except Exception:
        pass
    return os.environ.get(key)


# ── Hacker News ───────────────────────────────────────────────────────── #

HN_BASE = "https://hacker-news.firebaseio.com/v0"


def hn_show_stories(limit: int = 60) -> List[Dict]:
    """Fetch Show HN posts — founders announcing their own products."""
    r = requests.get(f"{HN_BASE}/showstories.json", headers=HEADERS, timeout=TIMEOUT)
    if not r.ok:
        return []
    ids = r.json()[:limit]
    items = []
    for story_id in ids:
        try:
            sr = requests.get(f"{HN_BASE}/item/{story_id}.json", headers=HEADERS, timeout=TIMEOUT)
            if sr.ok:
                data = sr.json()
                title = data.get("title", "")
                if title.lower().startswith("show hn"):
                    clean = title.replace("Show HN:", "").replace("Show HN: ", "").strip()
                    items.append({
                        "name": clean,
                        "description": title,
                        "url": data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "source": "Hacker News (Show HN)",
                    })
            time.sleep(0.05)
        except Exception:
            continue
    return items


def hn_new_stories(limit: int = 80) -> List[Dict]:
    """Fetch newest HN stories."""
    r = requests.get(f"{HN_BASE}/newstories.json", headers=HEADERS, timeout=TIMEOUT)
    if not r.ok:
        return []
    ids = r.json()[:limit]
    items = []
    for story_id in ids:
        try:
            sr = requests.get(f"{HN_BASE}/item/{story_id}.json", headers=HEADERS, timeout=TIMEOUT)
            if sr.ok:
                data = sr.json()
                title = data.get("title", "")
                if title:
                    items.append({
                        "name": title,
                        "description": title,
                        "url": data.get("url", ""),
                        "source": "Hacker News",
                    })
            time.sleep(0.05)
        except Exception:
            continue
    return items


# ── SEC EDGAR ─────────────────────────────────────────────────────────── #

EDGAR_BASE = "https://efts.sec.gov/LATEST/search-index"


def edgar_form_d(query: str, days_back: int = 60) -> List[Dict]:
    """Search recent Form D filings. days_back=60 for fresher signal."""
    start = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    params = {
        "q": f'"{query}"',
        "dateRange": "custom",
        "startdt": start,
        "forms": "D",
    }
    try:
        r = requests.get(EDGAR_BASE, headers=HEADERS, params=params, timeout=TIMEOUT)
        if not r.ok:
            return []
        hits = r.json().get("hits", {}).get("hits", [])
        items = []
        for hit in hits:
            src = hit.get("_source", {})
            name = src.get("entity_name", "")
            filed = src.get("file_date", "")
            amount = src.get("total_offering_amount", "")
            if name:
                desc = "SEC Form D — raised"
                if amount:
                    try:
                        desc += f" ${float(amount):,.0f}"
                    except Exception:
                        pass
                desc += f" | filed {filed}"
                items.append({
                    "name": name,
                    "description": desc,
                    "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={name}&type=D&dateb=&owner=include&count=10",
                    "source": "SEC EDGAR Form D",
                })
        return items
    except Exception:
        return []


def edgar_form_d_batch(terms: List[str], days_back: int = 60) -> List[Dict]:
    """Run edgar_form_d for a list of terms, deduplicated by company name."""
    seen: set = set()
    results = []
    for term in terms:
        for item in edgar_form_d(term, days_back=days_back):
            key = item["name"].strip().lower()
            if key not in seen:
                seen.add(key)
                results.append(item)
        time.sleep(0.1)
    return results


# ── RSS Parser ────────────────────────────────────────────────────────── #

def parse_rss(url: str, source_name: str = "RSS") -> List[Dict]:
    """Parse any RSS/Atom feed."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if not r.ok:
            return []
        root = ET.fromstring(r.content)
        items = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//item") or root.findall(".//atom:entry", ns)
        for entry in entries:
            title = (
                entry.findtext("title")
                or entry.findtext("atom:title", namespaces=ns)
                or ""
            ).strip()
            link = (
                entry.findtext("link")
                or entry.findtext("atom:link", namespaces=ns)
                or ""
            ).strip()
            desc = (
                entry.findtext("description")
                or entry.findtext("summary")
                or entry.findtext("atom:summary", namespaces=ns)
                or ""
            ).strip()
            if title:
                items.append({
                    "name": title,
                    "description": desc or title,
                    "url": link,
                    "source": source_name,
                })
        return items
    except Exception:
        return []


def parse_rss_batch(feeds: List[tuple]) -> List[Dict]:
    """Parse multiple RSS feeds. feeds = [(url, source_name), ...]"""
    results = []
    for url, name in feeds:
        results.extend(parse_rss(url, name))
    return results


# ── High-signal funding RSS (no key needed) ───────────────────────────── #

FUNDING_RSS_FEEDS = [
    ("https://news.crunchbase.com/feed/",                   "Crunchbase News"),
    ("https://techcrunch.com/tag/funding/feed/",            "TechCrunch Funding"),
    ("https://techcrunch.com/tag/startups/feed/",           "TechCrunch Startups"),
    ("https://venturebeat.com/category/business/feed/",     "VentureBeat"),
    ("https://eu-startups.com/feed/",                       "EU Startups"),
    ("https://www.geekwire.com/feed/",                      "GeekWire"),
    ("https://www.finsmes.com/feed",                        "FinSMEs Funding"),
    ("https://www.builtinchicago.org/rss.xml",              "Built In Chicago"),
    ("https://chicagoinno.streetinsider.com/rss",           "Chicago Inno"),
]


def fetch_funding_rss() -> List[Dict]:
    """Fetch all high-signal funding RSS feeds."""
    return parse_rss_batch(FUNDING_RSS_FEEDS)


# ── Product Hunt API ──────────────────────────────────────────────────── #

PH_API_URL = "https://api.producthunt.com/v2/api/graphql"


def producthunt_launches(days_back: int = 7, limit: int = 50) -> List[Dict]:
    """
    Fetch recent Product Hunt launches via GraphQL API.
    Requires PRODUCTHUNT_TOKEN in .streamlit/secrets.toml

    Setup (free):
    1. producthunt.com/v2/oauth/applications → create app
    2. Use client_credentials grant to get bearer token
    3. Add: PRODUCTHUNT_TOKEN = "your_token" to secrets.toml
    """
    token = _get_secret("PRODUCTHUNT_TOKEN")
    if not token:
        return []

    after_date = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%dT00:00:00Z")
    query = """
    query($after: DateTime, $first: Int) {
      posts(order: NEWEST, after: $after, first: $first) {
        edges {
          node {
            name
            tagline
            url
            website
            votesCount
            topics { edges { node { name } } }
          }
        }
      }
    }
    """
    try:
        r = requests.post(
            PH_API_URL,
            headers={**HEADERS, "Authorization": f"Bearer {token}",
                     "Content-Type": "application/json"},
            json={"query": query, "variables": {"after": after_date, "first": limit}},
            timeout=TIMEOUT,
        )
        if not r.ok:
            return []
        edges = r.json().get("data", {}).get("posts", {}).get("edges", [])
        items = []
        for edge in edges:
            node = edge.get("node", {})
            name = node.get("name", "")
            tagline = node.get("tagline", "")
            url = node.get("website") or node.get("url", "")
            topics = [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])]
            if name:
                items.append({
                    "name": name,
                    "description": f"{tagline} | topics: {', '.join(topics)}" if topics else tagline,
                    "url": url,
                    "source": "Product Hunt",
                })
        return items
    except Exception:
        return []


# ── Crunchbase API ────────────────────────────────────────────────────── #

CB_BASE = "https://api.crunchbase.com/api/v4"

STAGE_MAP = {
    "pre_seed": "Pre-Seed", "seed": "Seed",
    "angel": "Pre-Seed", "series_a": "Series A",
    "series_b": "Series B",
}


def crunchbase_recent_funding(days_back: int = 30, limit: int = 100) -> List[Dict]:
    """
    Fetch recent Pre-Seed/Seed/Series A rounds from Crunchbase.
    Requires CRUNCHBASE_KEY in secrets.toml.

    Free tier: crunchbase.com/pages/crunchbase-basic-access (500 req/month)
    Results cached 30min in Streamlit so you won't burn through quota.
    """
    key = _get_secret("CRUNCHBASE_KEY")
    if not key:
        return []

    after_date = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    payload = {
        "field_ids": ["identifier", "short_description", "last_funding_type",
                      "last_funding_at", "website_url"],
        "query": [
            {"type": "predicate", "field_id": "last_funding_at",
             "operator_id": "gte", "values": [after_date]},
            {"type": "predicate", "field_id": "last_funding_type",
             "operator_id": "includes",
             "values": ["pre_seed", "seed", "angel", "series_a"]},
        ],
        "order": [{"field_id": "last_funding_at", "sort": "desc"}],
        "limit": limit,
    }
    try:
        r = requests.post(
            f"{CB_BASE}/searches/organizations",
            headers={**HEADERS, "Content-Type": "application/json"},
            params={"user_key": key},
            json=payload,
            timeout=15,
        )
        if not r.ok:
            return []
        items = []
        for entity in r.json().get("entities", []):
            props = entity.get("properties", {})
            name = props.get("identifier", {}).get("value", "")
            desc = props.get("short_description", "")
            url = props.get("website_url", "")
            stage = STAGE_MAP.get(props.get("last_funding_type", ""), "")
            funded = props.get("last_funding_at", "")
            if name:
                items.append({
                    "name": name,
                    "description": f"{desc} | {stage} | funded {funded}".strip(" |"),
                    "url": url,
                    "source": "Crunchbase",
                    "funding_stage_hint": stage,
                })
        return items
    except Exception:
        return []


def crunchbase_search(query: str, days_back: int = 30) -> List[Dict]:
    """Search Crunchbase for companies matching a keyword with recent funding."""
    key = _get_secret("CRUNCHBASE_KEY")
    if not key:
        return []

    after_date = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    payload = {
        "field_ids": ["identifier", "short_description", "last_funding_type",
                      "last_funding_at", "website_url"],
        "query": [
            {"type": "predicate", "field_id": "facet_ids",
             "operator_id": "includes", "values": ["company"]},
            {"type": "predicate", "field_id": "last_funding_at",
             "operator_id": "gte", "values": [after_date]},
        ],
        "order": [{"field_id": "last_funding_at", "sort": "desc"}],
        "limit": 25,
    }
    try:
        r = requests.post(
            f"{CB_BASE}/searches/organizations",
            headers={**HEADERS, "Content-Type": "application/json"},
            params={"user_key": key, "q": query},
            json=payload,
            timeout=15,
        )
        if not r.ok:
            return []
        items = []
        for entity in r.json().get("entities", []):
            props = entity.get("properties", {})
            name = props.get("identifier", {}).get("value", "")
            desc = props.get("short_description", "")
            url = props.get("website_url", "")
            stage = STAGE_MAP.get(props.get("last_funding_type", ""), "")
            if name:
                items.append({
                    "name": name,
                    "description": desc or name,
                    "url": url,
                    "source": "Crunchbase",
                    "funding_stage_hint": stage,
                })
        return items
    except Exception:
        return []


# ── NewsAPI ───────────────────────────────────────────────────────────── #

def newsapi_search(query: str, days_back: int = 7, page_size: int = 50) -> List[Dict]:
    """Search NewsAPI for startup/funding headlines. Requires NEWSAPI_KEY."""
    key = _get_secret("NEWSAPI_KEY")
    if not key:
        return []
    start = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    try:
        r = requests.get(
            "https://newsapi.org/v2/everything",
            headers=HEADERS,
            params={"q": query, "from": start, "sortBy": "publishedAt",
                    "language": "en", "pageSize": page_size, "apiKey": key},
            timeout=TIMEOUT,
        )
        if not r.ok:
            return []
        return [
            {"name": a.get("title", ""),
             "description": a.get("description") or a.get("title", ""),
             "url": a.get("url", ""),
             "source": a.get("source", {}).get("name", "NewsAPI")}
            for a in r.json().get("articles", []) if a.get("title")
        ]
    except Exception:
        return []