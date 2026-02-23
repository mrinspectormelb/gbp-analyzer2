from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="GBP Gap Analyzer")

# Allow WordPress to call this API (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your WordPress domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class GBPRequest(BaseModel):
    keyword: str
    location: str
    target_business_name: str

def simulate_gbp_fetch(business_name, location):
    """
    Fake function to simulate fetching GBP data.
    Replace with Google API or scraping logic later.
    Returns a dict with categories, review_count, photos.
    """
    # Example mock data
    data = {
        "categories": ["Plumber", "Emergency Plumbing"],
        "review_count": 35,
        "photos": 12,
        "posts_per_month": 2
    }
    return data

def compute_gap_score(target, competitors):
    """
    Compute a simple gap score:
    - Missing categories, low reviews, few photos/posts reduce score
    """
    score = 100

    # Check categories
    competitor_categories = set()
    for c in competitors:
        competitor_categories.update(c["categories"])
    missing_categories = set(competitor_categories) - set(target["categories"])
    score -= len(missing_categories) * 10

    # Reviews
    avg_comp_reviews = sum(c["review_count"] for c in competitors) / len(competitors)
    if target["review_count"] < avg_comp_reviews:
        score -= 15

    # Photos
    avg_comp_photos = sum(c["photos"] for c in competitors) / len(competitors)
    if target["photos"] < avg_comp_photos:
        score -= 10

    # Posts
    avg_comp_posts = sum(c["posts_per_month"] for c in competitors) / len(competitors)
    if target["posts_per_month"] < avg_comp_posts:
        score -= 5

    return max(score, 0), missing_categories

@app.post("/analyze-gbp")
def analyze(data: GBPRequest):
    try:
        # Fetch target business data
        target_data = simulate_gbp_fetch(data.target_business_name, data.location)

        # Simulate 2 competitors for MVP
        competitors = [
            simulate_gbp_fetch("Competitor 1", data.location),
            simulate_gbp_fetch("Competitor 2", data.location)
        ]

        gap_score, missing_categories = compute_gap_score(target_data, competitors)

        # Build actions list dynamically
        actions = []

        for cat in missing_categories:
            actions.append(["HIGH", f"Add missing category: {cat}"])

        if target_data["review_count"] < sum(c["review_count"] for c in competitors)/len(competitors):
            actions.append(["HIGH", "Increase reviews to match competitors"])

        if target_data["photos"] < sum(c["photos"] for c in competitors)/len(competitors):
            actions.append(["MEDIUM", "Upload more photos"])

        if target_data["posts_per_month"] < sum(c["posts_per_month"] for c in competitors)/len(competitors):
            actions.append(["MEDIUM", "Post more updates monthly"])

        verdict = "Competitive" if gap_score >= 70 else "Uncompetitive"

        return {
            "gap_score": gap_score,
            "verdict": verdict,
            "actions": actions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
