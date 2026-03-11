"""
Scoring, stage detection, trend labeling, and rationale generation.
"""

import re
from typing import Dict

import pandas as pd


# ------------------------------------------------------------------ #
#  Funding stage detection                                             #
# ------------------------------------------------------------------ #

STAGE_PATTERNS = {
    "Pre-Seed": [r"\bpre[-\s]?seed\b", r"\$[0-9]+[kK]\b", r"\b[0-9]+[kK]\s+round\b"],
    "Seed": [r"\bseed\b", r"\bseed\s+round\b", r"\$[12]\s*[Mm]\b", r"\$[0-9]+\s*[Mm]\s+seed\b"],
    "Series A": [r"\bseries\s+a\b", r"\$[3-9]\s*[Mm]\b", r"\$1[0-5]\s*[Mm]\b"],
    "Series B": [r"\bseries\s+b\b", r"\$[2-9][0-9]\s*[Mm]\b"],
    "Series C+": [r"\bseries\s+[cdefg]\b", r"\$[1-9][0-9]{2}\s*[Mm]\b", r"\$[0-9]+\s*[Bb]\b"],
    "Growth": [r"\bgrowth\s+round\b", r"\blate[\s-]stage\b"],
}


def detect_funding_stage(row: pd.Series) -> str:
    text = f"{row.get('name', '')} {row.get('description', '')}".lower()
    for stage, patterns in STAGE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return stage
    return "Unknown"


# ------------------------------------------------------------------ #
#  Trend labeling                                                      #
# ------------------------------------------------------------------ #

TREND_KEYWORDS: Dict[str, list] = {
    "AI / ML": ["artificial intelligence", "machine learning", "llm", "generative ai", "gpt", "foundation model", "ai-powered", "ai agent"],
    "Embedded Finance": ["embedded finance", "banking-as-a-service", "baas", "embedded payments", "neobank"],
    "Climate / Sustainability": ["climate tech", "carbon", "net zero", "sustainability", "clean energy", "renewables", "esg"],
    "Web3 / Crypto": ["blockchain", "crypto", "defi", "nft", "web3", "dao", "token"],
    "Healthcare AI": ["digital health", "telehealth", "mental health tech", "medtech", "ai diagnostics", "wearable health"],
    "Supply Chain": ["supply chain", "last-mile", "fulfillment", "logistics automation", "inventory"],
    "Creator Economy": ["creator", "influencer", "monetization", "content platform"],
    "B2B SaaS": ["saas", "enterprise software", "workflow automation", "no-code", "low-code"],
    "Cybersecurity": ["cybersecurity", "zero trust", "identity", "soc", "threat detection"],
    "Space Tech": ["space", "satellite", "launch vehicle", "aerospace"],
}


def label_trends(row: pd.Series) -> str:
    text = f"{row.get('name', '')} {row.get('description', '')}".lower()
    matched = []
    for trend, keywords in TREND_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            matched.append(trend)
    return ", ".join(matched)


# ------------------------------------------------------------------ #
#  Scoring                                                             #
# ------------------------------------------------------------------ #

STAGE_SCORES = {
    "Pre-Seed": 5,
    "Seed": 4,
    "Series A": 3,
    "Series B": 2,
    "Series C+": 1,
    "Growth": 1,
    "Unknown": 0,
}


def score_company(row: pd.Series) -> float:
    score = 0.0

    # Stage preference (earlier = higher for most early-stage VCs)
    score += STAGE_SCORES.get(row.get("funding_stage", "Unknown"), 0)

    # Trend match
    trend = row.get("trend", "")
    if trend:
        score += len(trend.split(",")) * 1.5  # more trends = more signal

    # Portfolio overlap
    score += float(row.get("portfolio_overlap_score", 0)) * 3

    # Is already in portfolio
    if row.get("is_portfolio", False):
        score += 5

    return round(score, 2)


# ------------------------------------------------------------------ #
#  Rationale generation                                                #
# ------------------------------------------------------------------ #

def generate_rationale(row: pd.Series) -> str:
    parts = []

    stage = row.get("funding_stage", "Unknown")
    if stage != "Unknown":
        parts.append(f"{stage} stage")

    trend = row.get("trend", "")
    if trend:
        parts.append(f"trending in {trend}")

    closest = row.get("closest_portfolio_company", "")
    if closest and str(closest) != "nan":
        parts.append(f"semantically overlaps with {closest}")

    competitor = row.get("predicted_investor", "")
    if competitor and str(competitor) != "nan":
        parts.append(f"likely next investor: {competitor}")

    sector = row.get("sector", "")
    if sector:
        parts.append(f"sector: {sector}")

    return " · ".join(parts) if parts else "No signal detected"
