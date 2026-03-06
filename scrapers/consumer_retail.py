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

def scrape_consumer_retail():
    """Scrape consumer retail, fashion, and ecommerce startups."""
    urls = [
        "https://techcrunch.com/tag/fashion/",
        "https://techcrunch.com/category/ecommerce/",
        "https://vcnewsdaily.com/vcsearch.php",
        "https://dealroom.co",
        "https://www.fintechfutures.com/bankingtech/retail-banking",
        "https://www.businessoffashion.com/topics/retail/e-commerce/",
        "https://www.businessoffashion.com/topics/retail/resale-rental/",
        "https://www.businessoffashion.com/topics/technology/",
        "https://www.businessoffashion.com/news/luxury/prada-sales-climb-9-in-2025-as-versace-era-begins/",
        "https://www.vogue.com/business/sustainability",
        "https://www.vogue.com/business/fashion",
        "https://www.vogue.com/business/beauty",
        "https://www.vogue.com/business/technology"
    ]

    headers = {"User-Agent": "Mozilla/5.0"}
    companies = []

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for element in soup.find_all(["h3", "h2", "a"]):
                name = element.name.strip()

                company_name = extract_company_name(name)

                if name and len(name) > 5:
                    
                    company_name = extract_company_name(name)

                    companies.append({
                        "name": company_name,
                        "description": name,
                        "source": "Consumer Retail Scraper",
                        "sector": "Consumer Retail / Fashion / Ecommerce"
                    })
        except Exception as e:
            pass

    return pd.DataFrame(companies).drop_duplicates(subset=['name'])
