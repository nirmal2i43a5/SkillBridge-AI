from src.backend.db.repository import add_jobs
from src.recommender.recommender import JobPosting
from typing import Any

def index_jobs_from_payload(payload: dict) -> int:
    """Transform incoming payload into DB rows and persist."""
    #here we just pass list of dict 
    
    # payload["jobs"] is a list of dicts
    jobs_data = payload.get("jobs", [])
    if not jobs_data:
        return 0
        
    count = add_jobs(jobs_data)
    return count
