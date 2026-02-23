from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 👇 ALLOW WORDPRESS TO TALK TO THIS API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for testing ONLY
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    keyword: str
    location: str
    target_business_name: str

@app.post("/analyze-gbp")
def analyze(data: Request):
    return {
        "gap_score": 72,
        "verdict": "Uncompetitive",
        "actions": [
            ["HIGH", "Add missing GBP categories"],
            ["HIGH", "Get more reviews"],
            ["MEDIUM", "Upload photos weekly"]
        ]
    }