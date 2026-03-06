import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from datetime import datetime

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from io import BytesIO

TREND_KEYWORDS = {
    "DTC": ["dtc", "direct-to-consumer"],
    "Resale": ["resale", "recommerce"],
    "Clean Beauty": ["clean beauty", "non-toxic"],
    "Sustainable": ["sustainable", "circular"],
    "AI Healthcare": ["ai drug discovery", "generative ai in healthcare", "clinical workflow tools", "predictive analytics", "ai imaging", "data validation"],
    "Digital Health": ["remote patient monitoring", "rpm", "wearables", "telehealth 2.0", "patient-centric care platforms", "interoperability"],
    "Biotech": ["oncology", "neuroscience", "alzheimer's", "parkinson's", "regenerative therapies", "gene therapy", "mrna technology"],
    "MedTech": ["robotics", "smart diagnostics", "femtech", "onshoring", "supply chain resilience"],
    "Healthcare Operations": ["scalable business models", "regulatory compliance", "fda pathways", "value-based care", "clinical efficacy"],
    "Aging & Care Delivery": ["chronic disease management", "home healthcare solutions", "specialty care access"],
    # --- AI & DATA SYSTEMS ---

    "AI Agents & Autonomous Systems": [
        "agentic ai",
        "ai agents",
        "autonomous ai agents",
        "actionable ai systems"
    ],

    "Predictive Analytics & Forecasting": [
        "predictive analytics",
        "demand forecasting",
        "inventory forecasting",
        "supply chain analytics",
        "predictive diagnostics"
    ],

    "AI Personalization & Marketing": [
        "ai powered personalization",
        "ai personalization retail",
        "ai driven marketing",
        "data driven recommendations"
    ],

    # --- FINTECH ---

    "Generative AI in Finance": [
        "generative ai finance",
        "ai financial automation",
        "personalized financial insights ai",
        "generative ai compliance"
    ],

    "AI Underwriting & Fraud Detection": [
        "ai underwriting",
        "ai driven underwriting",
        "ai fraud detection",
        "fraud detection ai",
        "ai credit risk"
    ],

    "Blockchain Infrastructure & Tokenization": [
        "blockchain infrastructure",
        "asset tokenization",
        "tokenized real world assets",
        "blockchain financial infrastructure"
    ],

    "Embedded Finance & BaaS": [
        "embedded finance",
        "banking as a service",
        "baas",
        "embedded payments",
        "embedded lending"
    ],

    "Fintech Infrastructure & APIs": [
        "payment infrastructure",
        "api first fintech",
        "financial apis",
        "data aggregation fintech",
        "back office automation"
    ],

    "B2B Fintech & SME SaaS": [
        "b2b fintech",
        "sme fintech",
        "fintech saas",
        "accounting saas",
        "payroll saas"
    ],

    "Vertical Fintech": [
        "vertical fintech",
        "vertical saas fintech",
        "fintech for cfos",
        "industry specific fintech"
    ],

    "Real-time & Cross-border Payments": [
        "real time payments",
        "instant payments",
        "cross border payments",
        "international payments fintech"
    ],

    "RegTech & Compliance Tech": [
        "regtech",
        "automated compliance",
        "kyc automation",
        "aml automation",
        "kyb",
        "regulatory compliance software"
    ],

    "Data Privacy & Security": [
        "data privacy fintech",
        "financial data security",
        "cybersecurity fintech",
        "secure financial data"
    ],

    # --- LOGISTICS / SUPPLY CHAIN ---

    "AI Logistics & Control Towers": [
        "generative ai logistics",
        "logistics orchestration platform",
        "supply chain control tower",
        "real time logistics decision making"
    ],

    "Warehouse Robotics & Automation": [
        "autonomous mobile robots",
        "warehouse picking robots",
        "robotic warehouse picking",
        "automated warehouse storage"
    ],

    "ASRS Warehouse Systems": [
        "asrs",
        "automated storage retrieval system",
        "warehouse automation system"
    ],

    "Brownfield Warehouse Automation": [
        "brownfield automation",
        "legacy warehouse automation",
        "warehouse retrofit automation"
    ],

    "Micro Fulfillment Centers": [
        "micro fulfillment center",
        "automated micro fulfillment",
        "same day delivery fulfillment"
    ],

    "Supply Chain Visibility": [
        "supply chain visibility",
        "end to end logistics tracking",
        "real time shipment tracking"
    ],

    "Digital Twins Supply Chain": [
        "digital twin supply chain",
        "supply chain simulation",
        "logistics digital twin"
    ],

    "Logistics API & EDI Integration": [
        "edi logistics integration",
        "logistics api platform",
        "carrier integration api"
    ],

    "Blockchain Traceability": [
        "blockchain supply chain",
        "digital traceability logistics",
        "blockchain shipment tracking"
    ],

    "Green Logistics & Decarbonization": [
        "green logistics",
        "logistics decarbonization",
        "sustainable supply chain",
        "electric delivery fleets"
    ],

    "Carbon Tracking & Reporting": [
        "carbon tracking logistics",
        "supply chain emissions reporting"
    ],

    "Nearshoring & Regionalization": [
        "nearshoring supply chain",
        "regional manufacturing",
        "supply chain regionalization"
    ],

    "Reverse Logistics": [
        "reverse logistics",
        "returns management platform",
        "ecommerce returns logistics"
    ],

    "Digital Freight Marketplaces": [
        "digital freight brokerage",
        "freight marketplace",
        "ai freight matching"
    ],

    "3PL & 4PL Technology": [
        "3pl technology",
        "4pl logistics platform",
        "third party logistics software"
    ],

    "Logistics Workforce Automation": [
        "warehouse labor automation",
        "logistics workforce automation"
    ],

    # --- RETAIL / CPG / BEAUTY ---

    "Virtual Try-On & Diagnostics": [
        "virtual try on",
        "ar try on",
        "virtual skin diagnostics",
        "ai skin analysis"
    ],

    "Biotech Beauty": [
        "biotech beauty",
        "bioengineered ingredients",
        "lab grown ingredients",
        "synthetic biology beauty"
    ],

    "Sustainable Beauty & Packaging": [
        "sustainable packaging",
        "circular beauty",
        "zero waste beauty"
    ],

    "Clinical Skincare": [
        "clinical grade skincare",
        "science backed skincare",
        "dermatologist tested skincare"
    ],

    "Microbiome & Skin Health": [
        "skin microbiome",
        "microbiome friendly skincare",
        "probiotic skincare"
    ],

    "Functional Fragrance": [
        "functional fragrance",
        "wellness fragrance",
        "mood enhancing fragrance"
    ],

    "Hormonal & Menopause Beauty": [
        "menopause skincare",
        "hormonal skin solutions"
    ],

    "Recommerce & Resale": [
        "recommerce",
        "resale fashion",
        "secondhand marketplace"
    ],

    "Direct-to-Consumer Brands": [
        "direct to consumer",
        "dtc brand",
        "digital first brand"
    ],

    "Community-Driven Brands": [
        "community first brand",
        "creator led brand",
        "community driven commerce"
    ],

    "Supply Chain Optimization Retail": [
        "supply chain optimization",
        "inventory optimization retail"
    ],

    "Customer Loyalty & Retention": [
        "customer loyalty",
        "strong retention",
        "active customer engagement"
    ],

    # --- HEALTH TECH ---

    "AI Diagnostics & Medical Imaging": [
        "ai powered diagnostics",
        "ai medical imaging",
        "ai radiology",
        "early disease detection ai"
    ],

    "Clinical Workflow Automation": [
        "clinical workflow automation",
        "healthcare workflow automation",
        "hospital workflow optimization"
    ],

    "Remote Patient Monitoring": [
        "remote patient monitoring",
        "rpm healthcare",
        "home health monitoring"
    ],

    "Generative AI Drug Discovery": [
        "generative ai drug discovery",
        "ai drug discovery",
        "computational drug discovery"
    ],

    "Femtech": [
        "femtech",
        "womens health technology",
        "fertility technology"
    ],

    "Value-Based Care Platforms": [
        "value based care",
        "outcomes based healthcare"
    ],

    "Digital Therapeutics": [
        "digital therapeutics",
        "dtx",
        "software based treatment"
    ],

    "Healthcare Cybersecurity": [
        "healthcare cybersecurity",
        "patient data security",
        "hospital cybersecurity"
    ],

    "Healthcare Interoperability": [
        "healthcare interoperability",
        "ehr interoperability",
        "health data integration",
        "fhir integration"
    ],

    "Hospital at Home": [
        "hospital at home",
        "home based healthcare",
        "post acute care technology"
    ],

    "Personalized Medicine": [
        "personalized medicine",
        "precision medicine",
        "individualized treatment"
    ],

    "Medical Robotics": [
        "surgical robotics",
        "robotic surgery",
        "medical robotics"
    ],

    "Oncology & Immunology": [
        "oncology therapeutics",
        "immunotherapy",
        "precision oncology"
    ],

    "Neuroscience & Neurodegeneration": [
        "neurodegeneration research",
        "alzheimer treatment",
        "neuroscience therapeutics"
    ],

    "Digital Mental Health": [
        "digital mental health",
        "behavioral health platform",
        "online therapy platform"
    ],

    # --- INVESTOR SIGNALS / METRICS ---

    "VC Metrics & Signals": [
        "unit economics",
        "path to profitability",
        "capital efficient growth",
        "net retention",
        "recurring revenue",
        "product market fit",
        "scalable platform",
        "experienced founders",
        "strategic partnerships"
    ]
}


def _sanitize_field(val, max_len=10000):
    """Return a safe string for PDF generation.

    - convert NaN to empty string
    - enforce max length to avoid huge blobs that can crash reportlab
    - always return str
    """
    if pd.isna(val):
        return ""
    s = str(val)
    if len(s) > max_len:
        return s[:max_len] + "..."
    return s


def clean_data(dfs):
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset="name")
    df = df.dropna(subset=["name"])
    return df

def detect_funding_stage(row):
    desc = row["description"].lower()

    if "pre-seed" in desc:
        return "Pre-Seed"
    elif "seed" in desc:
        return "Seed"
    elif "angel" in desc:
        return "Angel"
    else:
        return "Unknown"

def generate_market_map(df):
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(df["description"])

    pca = PCA(n_components=2)
    coords = pca.fit_transform(X.toarray())

    df["x"] = coords[:, 0]
    df["y"] = coords[:, 1]

    return df

def generate_memo(company):
    """Generate a PDF memo and return its bytes.

    Returning raw bytes ensures Streamlit's download widget has a simple
    immutable object to handle instead of a file-like buffer which can
    sometimes behave oddly across reruns.
    """
    try:
        # sanitize all inputs so that reportlab doesn't choke on NaN/None/huge strings
        name = _sanitize_field(company.get("name", "Unnamed"), max_len=200)
        desc = _sanitize_field(company.get("description", ""))
        funding = _sanitize_field(company.get("funding_stage", "Unknown"))
        trend = _sanitize_field(company.get("trend", ""))
        overlap = company.get("portfolio_overlap", 0)
        try:
            overlap = float(overlap)
        except Exception:
            overlap = 0.0

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(name, styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(desc, styles["BodyText"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Funding Stage: {funding}", styles["BodyText"]))
        elements.append(Paragraph(f"Trend: {trend}", styles["BodyText"]))
        elements.append(Paragraph(f"Portfolio Overlap: {overlap:.2f}", styles["BodyText"]))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as exc:
        # re‑raise with additional context for the caller
        raise RuntimeError(f"error building memo for {company.get('name')} - {exc}")


def portfolio_overlap(df, portfolio_dict):

    portfolio_names = list(portfolio_dict.keys())
    portfolio_desc = list(portfolio_dict.values())

    overlap_scores = []
    closest_companies = []

    for desc in df["description"].fillna(""):

        corpus = [desc] + portfolio_desc

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(corpus)

        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        best_match_index = similarity.argmax()

        overlap_scores.append(similarity[best_match_index])
        closest_companies.append(portfolio_names[best_match_index])

    df["portfolio_overlap_score"] = overlap_scores
    df["closest_portfolio_company"] = closest_companies

    return df

def score_company(row):
    score = 0

    if row["funding_stage"] in ["Pre-Seed", "Seed"]:
        score += 4

    if row["trend"]:
        score += 3

    return score

def label_trends(row):
    desc = row["description"].lower()
    labels = []

    for trend, words in TREND_KEYWORDS.items():
        if any(w in desc for w in words):
            labels.append(trend)

    return ", ".join(labels)

def save_snapshot(df):
    df["snapshot_date"] = datetime.today().strftime("%Y-%m-%d")
    df.to_csv("data/historical_companies.csv", mode="a", index=False, header=False)

def compute_velocity():
    try:
        df = pd.read_csv("data/historical_companies.csv")
        return df.groupby("snapshot_date").size()
    except:
        return None