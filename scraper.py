from playwright.sync_api import sync_playwright
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
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            locale="en-AU"
        )

        page = context.new_page()

        search_url = f"https://www.google.com/maps/search/{keyword}+{location.replace(' ', '+')}"

        # --- Load page ---
        page.goto(search_url, timeout=60000)
        page.wait_for_timeout(6000)

        # --- Handle consent ---
        if "consent.google.com" in page.url:
            try:
                page.click("button:has-text('Accept')", timeout=5000)
            except:
                pass
            page.wait_for_timeout(5000)
            page.goto(search_url, timeout=60000)
            page.wait_for_timeout(8000)

        print("TITLE:", page.title())

        # --- Wait for results container ---
        page.wait_for_selector("div[role='feed']", timeout=20000)

        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(3000)

        link_elements = page.query_selector_all("a[href*='/maps/place/']")

        business_links = []

        for el in link_elements[:max_results]:
            href = el.get_attribute("href")
            if href and "/maps/place/" in href:
                business_links.append(href)

        for link in business_links:

            page.goto(link)
            page.wait_for_timeout(random.randint(4000, 6000))

            name = ""
            stars = 0.0
            reviews = 0

            try:
                name_el = page.query_selector("h1")
                if name_el:
                    name = name_el.inner_text()
            except:
                pass

            try:
                rating_el = page.query_selector("div[role='img'][aria-label*='stars']")
                if rating_el:
                    aria = rating_el.get_attribute("aria-label")
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

        browser.close()

    return results


def fetch_target_business_panel(business_name: str, location: str):
    results = scrape_google_maps(business_name, location, max_results=1)
    if not results:
        raise Exception("Target business not found")
    return results[0]
