import re

# ── UI / nav noise ───────────────────────────────────────────────────── #
BLOCKLIST = {
    "read more", "subscribe", "sign up", "log in", "login", "register",
    "home", "about", "contact", "privacy policy", "terms of service",
    "newsletter", "follow us", "share", "tweet", "more", "back", "next",
    "previous", "load more", "view all", "see all", "show more",
    "click here", "learn more", "get started", "try for free",
    "start free trial", "sign in", "advertise", "cookie policy",
    "terms", "accessibility", "sitemap", "©", "all rights reserved",
}

SOURCE_NOISE = {
    "techcrunch", "crunchbase", "axios", "reuters", "bloomberg",
    "the information", "pitchbook", "dealroom", "strictlyvc",
    "finsmes", "fintechfutures", "statnews", "medcitynews",
    "fiercehealthcare", "healthcaredive", "supplychaindive", "freightwaves",
    "vogue", "businessoffashion", "betalist", "product hunt",
    "m25", "chicago ventures", "hyde park ventures", "origin ventures",
}

BLOCKLIST |= SOURCE_NOISE

# ── Established / public companies that are NOT investment targets ───── #
# These are household names, public companies, and large enterprises that
# should never appear as "new startup" leads.
ESTABLISHED_COMPANIES = {
    # Big tech
    "microsoft", "google", "alphabet", "apple", "amazon", "meta", "netflix",
    "tesla", "nvidia", "intel", "amd", "ibm", "oracle", "salesforce", "sap",
    "adobe", "qualcomm", "broadcom", "cisco", "dell", "hp", "lenovo",
    "openai", "anthropic", "deepmind", "mistral",
    # Finance / payments
    "visa", "mastercard", "paypal", "stripe", "square", "block", "robinhood",
    "coinbase", "jpmorgan", "jp morgan", "goldman sachs", "morgan stanley",
    "bank of america", "wells fargo", "citibank", "citi", "american express",
    "amex", "charles schwab", "fidelity", "blackrock", "vanguard",
    # Retail / consumer
    "target", "walmart", "costco", "kroger", "amazon", "ebay", "etsy",
    "shopify", "wayfair", "chewy", "peloton", "nike", "adidas", "gap",
    "h&m", "zara", "inditex", "lvmh", "gucci", "prada", "burberry",
    "saks", "saks fifth avenue", "saks off 5th", "nordstrom", "macy's",
    "macys", "bloomingdales", "neiman marcus", "ralph lauren", "levi's",
    "levis", "uniqlo", "fast retailing",
    # Healthcare / pharma
    "pfizer", "moderna", "johnson & johnson", "j&j", "abbvie", "merck",
    "eli lilly", "bristol myers squibb", "astrazeneca", "novartis", "roche",
    "unitedhealth", "cvs", "walgreens", "anthem", "cigna", "humana",
    "mckesson", "cardinal health",
    # Media / telco
    "disney", "warner bros", "comcast", "at&t", "verizon", "t-mobile",
    "spotify", "twitter", "x", "linkedin", "youtube", "tiktok", "snapchat",
    "pinterest", "reddit",
    # Logistics / auto
    "fedex", "ups", "dhl", "usps", "maersk", "ford", "gm", "general motors",
    "toyota", "volkswagen", "bmw", "mercedes", "stellantis", "rivian",
    "lucid", "uber", "lyft", "doordash", "instacart", "grubhub",
    # Enterprise SaaS (already large)
    "servicenow", "workday", "zendesk", "hubspot", "twilio", "datadog",
    "snowflake", "databricks", "mongodb", "elastic", "cloudflare",
    "hashicorp", "confluent", "splunk", "dynatrace", "new relic",
    # Chicago-area large companies
    "boeing", "united airlines", "walgreens boots", "abbott", "baxter",
    "motorola", "groupon", "grubhub", "before brands",
    # Generic noise entities
    "sundar pichai", "elon musk", "sam altman", "jensen huang",
    "the fed", "federal reserve", "sec", "ftc", "doj",
}

# ── Keywords that signal genuine early-stage deal flow ───────────────── #
# An RSS item must contain at least one of these to be considered a lead.
FUNDING_SIGNAL_KEYWORDS = [
    "raises", "raised", "funding", "funded", "seed", "pre-seed", "preseed",
    "series a", "series b", "angel round", "venture", "vc", "backed",
    "investment", "invested", "investor", "closes", "closed", "secures",
    "secured", "launches", "launched", "debuts", "debut", "new startup",
    "early-stage", "early stage", "stealth", "spinout", "spin-out",
    "founded", "co-founded", "incubator", "accelerator", "y combinator",
    "techstars", "500 startups", "form d", "pre-launch",
]

# ── Headline verb patterns that signal the company is the subject ─────── #
FUNDING_PATTERNS = [
    r"^(.*?) raises",
    r"^(.*?) secures",
    r"^(.*?) lands",
    r"^(.*?) closes",
    r"^(.*?) bags",
    r"^(.*?) nabs",
    r"^(.*?) snags",
    r"^(.*?) gets \$",
    r"^(.*?) scores \$",
    r"^(.*?) launches",
    r"^(.*?) announces",
    r"^(.*?) unveils",
    r"^(.*?) debuts",
]


def extract_company_name(text: str) -> str:
    """Extract company name from funding-style headlines."""
    if not text:
        return ""
    for pattern in FUNDING_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return text.strip()


def has_funding_signal(text: str) -> bool:
    """Return True if the text contains any early-stage funding signal keyword."""
    lower = text.lower()
    return any(kw in lower for kw in FUNDING_SIGNAL_KEYWORDS)


def is_established_company(name: str) -> bool:
    """Return True if the name matches a known large / public company."""
    return name.strip().lower() in ESTABLISHED_COMPANIES


def is_valid_company_name(name: str) -> bool:
    """Return True if the string looks like a real, investable company name."""
    if not name or len(name) < 3 or len(name) > 120:
        return False

    if name.strip().isdigit():
        return False

    if name.strip().lower() in BLOCKLIST:
        return False

    # Block known large / established companies
    if is_established_company(name):
        return False

    # Block full article sentences (company names are rarely > 7 words)
    if len(name.split()) > 7:
        return False

    # Block strings that are purely punctuation / symbols
    if re.match(r'^[\W_]+$', name):
        return False

    # Block strings that look like article titles rather than names:
    # they tend to contain conjunctions, prepositions, or possessive phrases mid-string
    article_patterns = [
        r"\b(how|why|when|what|where|who|the|and|but|for|with|over|amid|after|before|during|inside|behind|against)\b",
        r"'s (?:ceo|cto|coo|founder|chief|new|latest|plan|strategy|move|bid|push|deal|exec)\b",
        r"\d{4}",         # year mentions like "2024 outlook"
        r"\$\d+[MBK]? \w+ \w+",  # dollar amounts mid-sentence
    ]
    for pat in article_patterns:
        if re.search(pat, name, re.IGNORECASE):
            return False

    return True


def normalize_name(name: str) -> str:
    """Lowercase + strip for deduplication purposes."""
    return name.strip().lower()