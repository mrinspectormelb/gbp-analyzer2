page.goto(search_url, timeout=60000)

# Wait initial load
page.wait_for_timeout(6000)

# Handle consent redirect
if "consent.google.com" in page.url:
    try:
        page.click("button:has-text('Accept all')", timeout=5000)
    except:
        try:
            page.click("button:has-text('Accept')", timeout=5000)
        except:
            pass

    page.wait_for_timeout(5000)

# Force reload to real Maps app
page.goto(search_url, timeout=60000)
page.wait_for_timeout(8000)

print("FINAL URL:", page.url)
print("FINAL TITLE:", page.title())
print("HTML CHECK:", page.content()[:500])

# Now wait for Maps app container instead of link selector
page.wait_for_selector("div[role='feed']", timeout=20000)
