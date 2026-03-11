import requests
import pandas as pd
import re
from bs4 import BeautifulSoup


def extract_company_name(text):
    """Extract company name from funding-style headlines.
    
    - If a funding pattern exists (raises, secures, launches, etc.), return the matched company name.
    - If no pattern exists, return the full original text.
    """
    
    # common startup headline patterns
    patterns = [
        r"^(.*?) raises",
        r"^(.*?) secures",
        r"^(.*?) lands",
        r"^(.*?) closes",
        r"^(.*?) bags",
        r"^(.*?) gets",
        r"^(.*?) launches"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()  # return only the company name
    
    # fallback: pattern not found, return the full text
    return text.strip()

def scrape_healthcare():
    """Scrape healthcare startups across multiple sources."""

    urls = [
        "https://techcrunch.com/category/healthcare/",
        "https://dealroom.co",
        "https://www.statnews.com/category/health-tech/",
        "https://medcitynews.com/category/channel/health-tech/?utm_source=mn-1",
        "https://www.axios.com/pro/all-deals?audienceSlugs=biotech-deals",
        "https://www.fiercehealthcare.com/health-tech",
        "https://www.healthcaredive.com/",
        "https://www.crunchbase.com/discover/organization.companies?mollie_params=%7B%22f_categories%22:%22healthcare%22%7D"
    ]

    headers = {"User-Agent": "Mozilla/5.0"}
    companies = []

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup.find_all(["h3", "h2", "a"]):
                text = element.text.strip()
                company_name = extract_company_name(text)

                if text and len(text) > 5:

                    companies.append({
                        "name": company_name,
                        "description": text,
                        "source": "Healthcare Scraper",
                        "sector": "Healthcare"
                    })

        except Exception:
            pass

    return pd.DataFrame(companies).drop_duplicates(subset=["name"])