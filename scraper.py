import requests
from bs4 import BeautifulSoup
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}

def scrape_google_maps(keyword: str, location: str, max_results=5):
    """Scrape top competitors from Google Maps search (public data only)."""
    search_url = f"https://www.google.com/maps/search/{keyword}+{location.replace(' ', '+')}"
    response = requests.get(search_url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Google Maps request failed: {response.status_code}")

    soup = BeautifulSoup(response.text, "lxml")
    results = []

    # Heuristic: find business name divs (replace with better parsing later)
    businesses = soup.find_all("div", string=re.compile(keyword, re.I))
    for b in businesses[:max_results]:
        name = b.get_text().strip()
        business = {
            "name": name,
            "categories": [keyword],
            "reviews": 0,          # parse real review count here
            "stars": 0.0,          # parse stars here
            "photos": 0,           # parse photo count
            "posts_per_month": 0,  # estimate from posts if visible
            "keywords_in_reviews": []  # extract common words
        }
        results.append(business)
        time.sleep(0.5)
    return results

def fetch_target_business_panel(business_name: str, location: str):
    """Scrape the target business panel from Google Maps."""
    query = f"{business_name} {location}".replace(" ", "+")
    url = f"https://www.google.com/maps/search/{query}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Google Maps request failed: {response.status_code}")

    soup = BeautifulSoup(response.text, "lxml")

    # Heuristic: find the exact business panel
    panel = soup.find("div", string=re.compile(business_name, re.I))
    if not panel:
        panel = soup.find("div", string=re.compile(location.split()[0], re.I))
        if not panel:
            raise Exception("Target business panel not found")

    target_data = {
        "name": business_name,
        "categories": [business_name],  # replace with parsed categories
        "reviews": 0,                   # parse review count
        "stars": 0.0,                   # parse star rating
        "photos": 0,                     # parse photo count
        "posts_per_month": 0,            # estimate
        "keywords_in_reviews": []        # extract keywords
    }
    time.sleep(0.5)
    return target_data
