from playwright.sync_api import sync_playwright
import time
import random
import re

def scrape_google_maps(keyword, location, max_results=5):

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
    headless=True,
    channel="chromium",   # IMPORTANT
    args=[
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ]
)

        page = browser.new_page()

        url = f"https://www.google.com/maps/search/{keyword}+{location.replace(' ', '+')}"
        page.goto(url)

        # wait for listings to load
        page.wait_for_selector("div[role='article']")

        listings = page.query_selector_all("div[role='article']")

        for listing in listings[:max_results]:

            name_el = listing.query_selector("div.fontHeadlineSmall")
            rating_el = listing.query_selector("span[aria-label*='stars']")

            name = name_el.inner_text() if name_el else "Unknown"
            stars = 0.0
            reviews = 0

            if rating_el:
                aria = rating_el.get_attribute("aria-label")
                match = re.search(r"(\d\.\d).*?(\d+)", aria)
                if match:
                    stars = float(match.group(1))
                    reviews = int(match.group(2))

            results.append({
                "name": name,
                "categories": [],
                "reviews": reviews,
                "stars": stars,
                "photos": 0,
                "posts_per_month": 0,
                "keywords_in_reviews": []
            })

        browser.close()

    return results


def fetch_target_business_panel(business_name, location):

    results = scrape_google_maps(business_name, location, 1)

    if not results:
        raise Exception("Target business not found")

    return results[0]
