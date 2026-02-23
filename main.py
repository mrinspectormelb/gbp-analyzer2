from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import scrape_google_maps, fetch_target_business_panel

app = FastAPI(title="GBP Gap Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your WP domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class GBPRequest(BaseModel):
    keyword: str
    location: str
    target_business_name: str

def compute_gap_score(target, competitors):
    score = 100
    if not competitors:
        return score, []

    avg_reviews = sum(c["reviews"] for c in competitors)/len(competitors)
    avg_photos = sum(c["photos"] for c in competitors)/len(competitors)
    avg_posts = sum(c["posts_per_month"] for c in competitors)/len(competitors)

    missing_categories = []
    competitor_categories = set(cat for c in competitors for cat in c["categories"])
    for cat in competitor_categories:
        if cat not in target["categories"]:
            missing_categories.append(cat)
            score -= 10

    if target["reviews"] < avg_reviews:
        score -= 15
    if target["stars"] < sum(c["stars"] for c in competitors)/len(competitors):
        score -= 10
    if target["photos"] < avg_photos:
        score -= 10
    if target["posts_per_month"] < avg_posts:
        score -= 5

    return max(score,0), missing_categories

@app.post("/analyze-gbp")
def analyze(data: GBPRequest):
    try:
        competitors = scrape_google_maps(data.keyword, data.location, max_results=5)
        target = fetch_target_business_panel(data.target_business_name, data.location)

        gap_score, missing_categories = compute_gap_score(target, competitors)

        actions = []
        for cat in missing_categories:
            actions.append(["HIGH", f"Add missing category: {cat}"])
        if target["reviews"] < sum(c["reviews"] for c in competitors)/len(competitors):
            actions.append(["HIGH", "Increase reviews to match competitors"])
        if target["photos"] < sum(c["photos"] for c in competitors)/len(competitors):
            actions.append(["MEDIUM", "Upload more photos"])
        if target["posts_per_month"] < sum(c["posts_per_month"] for c in competitors)/len(competitors):
            actions.append(["MEDIUM", "Post updates monthly"])

        verdict = "Competitive" if gap_score >= 70 else "Uncompetitive"

        return {
            "target_business": target["name"],
            "location": data.location,
            "gap_score": gap_score,
            "verdict": verdict,
            "competitor_comparison": competitors,
            "gap_summary": actions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
