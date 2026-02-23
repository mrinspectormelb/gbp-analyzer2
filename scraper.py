import requests
from bs4 import BeautifulSoup
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}

def fetch_target_business_panel(business_name: str, location: str):
    """
    Fetch basic info for a specific business from Google Maps search.
    Public data only.
    """
    query = f"{business_name} {location}".replace(" ", "+")
    url = f"https://www.google.com/maps/search/{query}"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Google Maps request failed: {response.status_code}")
    
    soup = BeautifulSoup(response.text, "lxml")

    # Heuristic parsing: find business name in the search results
    panel = soup.find("div", string=re.compile(business_name, re.I))
    if not panel:
        # fallback: use first search result
        panel = soup.find("div", string=re.compile(location.split()[0], re.I))
        if not panel:
            raise Exception("Target business panel not found")
    
    # Extract pseudo-real data (replace with real parsing later)
    target_data = {
        "name": business_name,
        "categories": ["Plumber"],  # placeholder for now
        "reviews": 0,
        "stars": 0,
        "photos": 0,
        "posts_per_month": 0,
        "keywords_in_reviews": []
    }

    # Extract approximate reviews/stars if present
    review_span = soup.find("span", string=re.compile(r"\d+ reviews", re.I))
    if review_span:
        m = re.search(r"(\d+) reviews", review_span.text)
        if m:
            target_data["reviews"] = int(m.group(1))
    
    star_span = soup.find("span", string=re.compile(r"\d(\.\d)?/5", re.I))
    if star_span:
        m = re.search(r"(\d(\.\d)?)/5", star_span.text)
        if m:
            target_data["stars"] = float(m.group(1))
    
    # TODO: extract photos count / posts / review keywords later

    time.sleep(0.5)  # polite delay
    return target_data
