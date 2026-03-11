import requests
from bs4 import BeautifulSoup
import pandas as pd

import re


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

def scrape_betalist():

    url = "https://betalist.com/startups"
    headers = {"User-Agent": "Mozilla/5.0"}

    companies = []

    try:

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Each startup appears in a startup card
        cards = soup.select("div.startup")

        for card in cards:

            name_tag = card.select_one("h3")
            desc_tag = card.select_one("p")

            if name_tag:

                name = name_tag.text.strip()
                company_name = extract_company_name(name) 

                description = ""
                if desc_tag:
                    description = desc_tag.text.strip()

                companies.append({
                    "name": company_name,
                    "description": description,
                    "source": "BetaList",
                    "sector": "Startup"
                })

    except Exception as e:
        print("BetaList scrape failed:", e)

    return pd.DataFrame(companies).drop_duplicates(subset=["name"])


def scrape_producthunt():
    """Scrape new tech products from Product Hunt."""

    url = "https://www.producthunt.com/stories/category/announcements"
    headers = {"User-Agent": "Mozilla/5.0"}

    companies = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Product cards typically appear as links with product titles
        cards = soup.select("a[data-test='post-name']")

        for card in cards:

            name = card.text.strip()

            if name and len(name) > 2:

                # description is usually in sibling span
                parent = card.find_parent()
                company_name = extract_company_name(name) 

                description = ""
                if parent:
                    desc_tag = parent.find("span")
                    if desc_tag:
                        description = desc_tag.text.strip()

                companies.append({
                    "name": company_name,
                    "description": description,
                    "source": "Product Hunt",
                    "sector": "Tech Product"
                })

    except Exception as e:
        print("Product Hunt scrape failed:", e)

    return pd.DataFrame(companies).drop_duplicates(subset=["name"])