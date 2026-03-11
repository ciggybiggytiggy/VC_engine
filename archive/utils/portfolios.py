import requests
from bs4 import BeautifulSoup

def scrape_chicago_ventures_portfolio():
    url = "https://www.chicagoventures.com/companies"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    portfolio = {}

    # Assuming companies are in cards with h3 or h4 for names
    cards = soup.find_all(['h3', 'h4'])

    for card in cards:
        name = card.text.strip()
        if name and len(name) > 2 and len(name.split()) <= 3:
            parent = card.find_parent()
            description = parent.get_text() if parent else name
            description = description.replace(name, '').strip()
            if description:
                portfolio[name] = description
            else:
                portfolio[name] = name  # fallback

    return portfolio


def scrape_hyde_park_portfolio():
    url = "https://www.hydeparkvp.com/companies"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    portfolio = {}

    # Assuming companies are in cards with h3 or h4 for names
    cards = soup.find_all(['h3', 'h4'])

    for card in cards:
        name = card.text.strip()
        if name and len(name) > 2 and len(name.split()) <= 3:
            parent = card.find_parent()
            description = parent.get_text() if parent else name
            description = description.replace(name, '').strip()
            if description:
                portfolio[name] = description
            else:
                portfolio[name] = name  # fallback

    return portfolio


def scrape_m25_portfolio():
    url = "https://www.m25vc.com/portfolio"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    portfolio = {}

    # Assuming companies are in cards with h3 or h4 for names
    cards = soup.find_all(['h3', 'h4'])

    for card in cards:
        name = card.text.strip()
        if name and len(name) > 2 and len(name.split()) <= 3:
            parent = card.find_parent()
            description = parent.get_text() if parent else name
            # Clean up: remove extra text, perhaps split or extract relevant part
            description = description.replace(name, '').strip()
            if description:
                portfolio[name] = description
            else:
                portfolio[name] = name  # fallback

    return portfolio


def scrape_origin_ventures():
    url = "https://www.originventures.com/portfolio"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    portfolio = {}

    # Assuming companies are in cards with h3 or h4 for names
    cards = soup.find_all(['h3', 'h4'])

    for card in cards:
        name = card.text.strip()
        if name and len(name) > 2 and len(name.split()) <= 3:
            parent = card.find_parent()
            description = parent.get_text() if parent else name
            description = description.replace(name, '').strip()
            if description:
                portfolio[name] = description
            else:
                portfolio[name] = name  # fallback

    return portfolio
