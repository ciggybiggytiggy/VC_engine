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
        if name:  # skip empty
            # Find description in parent or sibling
            parent = card.find_parent()
            description = parent.get_text() if parent else name
            # Clean up: remove extra text, perhaps split or extract relevant part
            description = description.replace(name, '').strip()
            if description:
                portfolio[name] = description
            else:
                portfolio[name] = name  # fallback

    return portfolio

# For backward compatibility, keep the static one or replace
chicago_ventures_portfolio = scrape_chicago_ventures_portfolio()