from playwright.sync_api import sync_playwright
import time
import random
import re


def scrape_google_maps(keyword: str, location: str, max_results=5):

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            channel="chromium",
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = browser.new_page(
            viewport={
                "width": random.randint(1280, 1600),
                "height": random.randint(700, 1000)
            },
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )

        search_url = f"https://www.google.com/maps/search/{keyword}+{location.replace(' ', '+')}"

        page.goto(search_url, timeout=60000)

        # Give page time to load
        page.wait_for_timeout(5000)

        # Handle Google consent screen if shown
        try:
            page.click("button:has-text('Accept')", timeout=5000)
            page.wait_for_timeout(2000)
        except:
            pass

        # Wait for business links instead of fragile layout selectors
        page.wait_for_selector("a[href*='/maps/place/']", timeout=20000)

        listings = page.query_selector_all("a[href*='/maps/place/']")

        for listing in listings[:max_results]:

            name = listing.inner_text().strip()

            # Click into listing for detailed info
            listing.click()
            page.wait_for_timeout(4000)

            stars = 0.0
            reviews = 0

            try:
                rating_element = page.query_selector("div[role='img'][aria-label*='stars']")
                if rating_element:
                    aria = rating_element.get_attribute("aria-label")
                    match = re.search(r"(\d\.\d).*?(\d+)", aria)
                    if match:
                        stars = float(match.group(1))
                        reviews = int(match.group(2))
            except:
                pass

            results.append({
                "name": name,
                "categories": [],
                "reviews": reviews,
                "stars": stars,
                "photos": 0,
                "posts_per_month": 0,
                "keywords_in_reviews": []
            })

            # Go back to results
            page.go_back()
            page.wait_for_timeout(random.randint(2000, 4000))

        browser.close()

    return results


def fetch_target_business_panel(business_name: str, location: str):

    results = scrape_google_maps(business_name, location, max_results=1)

    if not results:
        raise Exception("Target business not found")

    return results[0]
