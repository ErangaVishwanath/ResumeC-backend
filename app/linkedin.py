import requests
from fastapi import HTTPException

def linkedin_scraper(profile_url: str, linkedin_token: str):
    headers = {"Authorization": f"Bearer {linkedin_token}"}
    
    # Get profile data
    linkedin_api = "https://api.linkedin.com/v2/me"
    profile_response = requests.get(linkedin_api, headers=headers)

    if profile_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid LinkedIn token")
    profile_data = profile_response.json()

    # Get experience positions
    experience_api = "https://api.linkedin.com/v2/positions"
    exp_response = requests.get(experience_api, headers=headers)

    linkedin_experience = []
    if exp_response.status_code == 200:
        exp_data = exp_response.json()
        linkedin_experience = [
            {
                "title": pos.get("title"),
                "company": pos.get("companyName"),
                "start": pos.get("timePeriod", {}).get("startDate"),
                "end": pos.get("timePeriod", {}).get("endDate")
            }
            for pos in exp_data.get("elements", [])
        ]
    
    return {
        "profile": profile_data,
        "experience": linkedin_experience
    }