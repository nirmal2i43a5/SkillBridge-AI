from src.backend.db.repository import add_jobs
from src.recommender.recommender import JobPosting
from sqlalchemy.orm import Session

def index_jobs_from_payload(payload: dict, db: Session) -> int:
    """Transform incoming payload into DB rows and persist."""
    #here we just pass list of dict 
    
    # payload["jobs"] is a list of dicts
    jobs_data = payload.get("jobs", [])
    if not jobs_data:
        return 0
        
    count = add_jobs(jobs_data, db)
    return count
