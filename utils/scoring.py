"""
Scoring, stage detection, trend labeling, and rationale generation.
Aligned to Chicago Ventures' thesis: B2B SaaS, Fintech, Healthcare,
Supply Chain/Logistics, and Chicago-area founding teams.
"""

import re
from typing import Dict

import pandas as pd


# ------------------------------------------------------------------ #
#  Funding stage detection                                             #
# ------------------------------------------------------------------ #

STAGE_PATTERNS = {
    "Pre-Seed": [r"\bpre[-\s]?seed\b", r"\$[0-9]+[kK]\b", r"\b[0-9]+[kK]\s+round\b"],
    "Seed":     [r"\bseed\b", r"\bseed\s+round\b", r"\$[12]\s*[Mm]\b", r"\$[0-9]+\s*[Mm]\s+seed\b"],
    "Series A": [r"\bseries\s+a\b", r"\$[3-9]\s*[Mm]\b", r"\$1[0-5]\s*[Mm]\b"],
    "Series B": [r"\bseries\s+b\b", r"\$[2-9][0-9]\s*[Mm]\b"],
    "Series C+": [r"\bseries\s+[cdefg]\b", r"\$[1-9][0-9]{2}\s*[Mm]\b", r"\$[0-9]+\s*[Bb]\b"],
    "Growth":   [r"\bgrowth\s+round\b", r"\blate[\s-]stage\b"],
}

# Amount ranges from structured EDGAR data → stage inference
# Used when detect_funding_stage returns Unknown but amount_raised is present
AMOUNT_STAGE_RANGES = [
    (0,        250_000,   "Pre-Seed"),
    (250_001,  2_000_000, "Seed"),
    (2_000_001,15_000_000,"Series A"),
    (15_000_001,50_000_000,"Series B"),
    (50_000_001,float("inf"), "Series C+"),
]


def _parse_amount(amount_str: str) -> float:
    """Parse '$1,250,000' or '$2M' style strings to float. Returns 0 on failure."""
    if not amount_str:
        return 0.0
    s = str(amount_str).replace(",", "").replace("$", "").strip()
    try:
        if s.endswith("M") or s.endswith("m"):
            return float(s[:-1]) * 1_000_000
        if s.endswith("K") or s.endswith("k"):
            return float(s[:-1]) * 1_000
        if s.endswith("B") or s.endswith("b"):
            return float(s[:-1]) * 1_000_000_000
        return float(s)
    except ValueError:
        return 0.0


def detect_funding_stage(row: pd.Series) -> str:
    # First try text patterns
    text = f"{row.get('name', '')} {row.get('description', '')}".lower()
    for stage, patterns in STAGE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return stage

    # Fall back to structured amount_raised from EDGAR if available
    amount = _parse_amount(row.get("amount_raised", ""))
    if amount > 0:
        for lo, hi, stage in AMOUNT_STAGE_RANGES:
            if lo <= amount <= hi:
                return stage

    return "Unknown"


# ------------------------------------------------------------------ #
#  Trend labeling — aligned to Chicago Ventures portfolio clusters     #
# ------------------------------------------------------------------ #

TREND_KEYWORDS: Dict[str, list] = {
    # Chicago Ventures thesis sectors
    "B2B SaaS": [
        "saas", "enterprise software", "workflow automation", "no-code", "low-code",
        "b2b software", "vertical saas", "api platform", "devtools", "developer tools",
        "platform", "dashboard", "productivity", "collaboration tool",
    ],
    "Fintech": [
        "fintech", "payments", "neobank", "embedded finance", "banking-as-a-service",
        "baas", "embedded payments", "insurtech", "wealthtech", "lending", "credit",
        "payroll", "treasury", "invoice financing", "buy now pay later", "bnpl",
        "open banking", "remittance", "cross-border payments",
    ],
    "Healthcare / MedTech": [
        "digital health", "telehealth", "medtech", "healthtech", "mental health",
        "behavioral health", "care coordination", "clinical", "diagnostics",
        "wearable health", "pharmacy", "drug discovery", "patient", "ehr",
        "population health", "women's health", "home health",
    ],
    "Supply Chain / Logistics": [
        "supply chain", "last-mile", "last mile", "fulfillment", "logistics",
        "freight", "warehouse", "inventory", "shipping", "fleet management",
        "route optimization", "3pl", "cold chain", "procurement", "reverse logistics",
        "autonomous delivery", "dark store", "micro-fulfillment",
    ],
    "AI / ML": [
        "artificial intelligence", "machine learning", "llm", "generative ai",
        "foundation model", "ai agent", "ai-powered", "large language model",
        "computer vision", "nlp", "natural language", "predictive analytics",
        "ai automation",
    ],
    # Emerging themes Chicago Ventures has signaled interest in
    "Construction / PropTech": [
        "construction tech", "proptech", "real estate tech", "building tech",
        "permitting", "contractor", "workforce management construction",
        "smart building", "facility management", "architecture tech",
    ],
    "Restaurant / FoodTech": [
        "restaurant tech", "foodtech", "food delivery", "meal kit", "pos system",
        "online ordering", "ghost kitchen", "food and beverage", "beverage",
        "grocery tech", "food safety",
    ],
    "Climate / Sustainability": [
        "climate tech", "carbon", "net zero", "sustainability", "clean energy",
        "renewables", "esg", "cleantech", "circular economy", "green",
    ],
    "Creator Economy": [
        "creator", "influencer", "monetization", "content platform", "newsletter",
        "community platform", "audience", "social commerce",
    ],
    "Cybersecurity": [
        "cybersecurity", "zero trust", "identity", "soc", "threat detection",
        "data security", "compliance automation", "infosec",
    ],
}


def label_trends(row: pd.Series) -> str:
    text = f"{row.get('name', '')} {row.get('description', '')}".lower()
    matched = []
    for trend, keywords in TREND_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            matched.append(trend)
    return ", ".join(matched)


# ------------------------------------------------------------------ #
#  Geography detection                                                 #
# ------------------------------------------------------------------ #

CHICAGO_GEO_SIGNALS = {
    "illinois", "chicago", "evanston", "naperville", "oak park",
    "schaumburg", "downers grove", "lisle", "skokie", "waukegan",
    "joliet", "champaign", "urbana", "peoria", "rockford",
    "il ", " il,", "(il)", "chicago, il", "chicago il",
}


def is_chicago_area(row: pd.Series) -> bool:
    """
    Return True if any available field suggests a Chicago-area company.

    Deliberately excludes `sector` — every row from BuiltInChicagoScraper
    has sector='Chicago Startup' which would cause false positives for
    Berlin, Milan, Singapore etc. companies pulled from global RSS feeds.

    Also excludes `source` — source names like 'Built In Chicago' would
    similarly flag every row regardless of company location.

    Reliable fields only: EDGAR state, company name, description, url.
    """
    # EDGAR structured state field — most reliable signal
    state = str(row.get("state", "")).strip().lower()
    if state in ("il", "illinois"):
        return True

    # Check name, description, and url only — not sector or source
    full_text = (
        f"{row.get('name', '')} "
        f"{row.get('description', '')} "
        f"{row.get('url', '')}"
    ).lower()

    return any(sig in full_text for sig in CHICAGO_GEO_SIGNALS)


# ------------------------------------------------------------------ #
#  Scoring — Chicago Ventures thesis-aligned                           #
# ------------------------------------------------------------------ #

STAGE_SCORES = {
    "Pre-Seed": 5,
    "Seed":     4,
    "Series A": 3,
    "Series B": 2,
    "Series C+": 1,
    "Growth":   1,
    "Unknown":  0,
}

# Sectors that align tightly with Chicago Ventures' portfolio
CV_THESIS_SECTORS = {
    "B2B SaaS", "Fintech", "Healthcare / MedTech",
    "Supply Chain / Logistics", "Construction / PropTech",
    "Restaurant / FoodTech",
}


def score_company(row: pd.Series) -> float:
    score = 0.0

    # 1. Stage (0–5) — earlier is better for CV's pre-seed/seed mandate
    score += STAGE_SCORES.get(row.get("funding_stage", "Unknown"), 0)

    # 2. Trend match — weight thesis sectors more heavily
    trend = row.get("trend", "")
    if trend:
        matched_trends = [t.strip() for t in trend.split(",") if t.strip()]
        for t in matched_trends:
            if t in CV_THESIS_SECTORS:
                score += 2.0   # thesis-aligned trend
            else:
                score += 0.75  # adjacent signal, less weight

    # 3. Portfolio semantic overlap (0–1 cosine similarity, scaled to 0–3)
    score += float(row.get("portfolio_overlap_score", 0)) * 3

    # 4. Chicago geography bonus — CV explicitly focuses on midwest
    if is_chicago_area(row):
        score += 2.0

    # 5. Already in portfolio (monitor, not invest — lower bonus than geography)
    if row.get("is_portfolio", False):
        score += 1.0

    # 6. Has structured raise amount — signals a real filing, not just noise
    if row.get("amount_raised", ""):
        score += 0.5

    return round(score, 2)


# ------------------------------------------------------------------ #
#  Rationale generation                                                #
# ------------------------------------------------------------------ #

def generate_rationale(row: pd.Series) -> str:
    parts = []

    stage = row.get("funding_stage", "Unknown")
    if stage != "Unknown":
        parts.append(f"{stage} stage")

    amount = row.get("amount_raised", "")
    if amount:
        parts.append(f"raised {amount}")

    if is_chicago_area(row):
        parts.append("Chicago-area")

    trend = row.get("trend", "")
    if trend:
        # Highlight thesis-aligned trends first
        trends = [t.strip() for t in trend.split(",") if t.strip()]
        thesis = [t for t in trends if t in CV_THESIS_SECTORS]
        other = [t for t in trends if t not in CV_THESIS_SECTORS]
        ordered = thesis + other
        parts.append(f"trending: {', '.join(ordered[:3])}")

    closest = row.get("closest_portfolio_company", "")
    if closest and str(closest) not in ("nan", ""):
        parts.append(f"similar to {closest}")

    competitor = row.get("predicted_investor", "")
    if competitor and str(competitor) not in ("nan", ""):
        parts.append(f"watch: {competitor}")

    source = row.get("source", "")
    if source:
        parts.append(f"via {source}")

    return " · ".join(parts) if parts else "No signal detected"