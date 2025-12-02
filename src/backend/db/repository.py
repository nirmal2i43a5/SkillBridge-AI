import json
from typing import List, Any
from sqlalchemy.orm import Session
from .models import Job

def safe_str(val: Any) -> str | None:
    if val is None:
        return None
    if isinstance(val, list):
        return ", ".join(map(str, val))
    return str(val)

def add_jobs(job_dicts: List[dict], db: Session) -> int:
    """Insert many jobs; ignore duplicates (same job_id). Returns number inserted."""
    inserted = 0
    seen_in_batch = set()
    
    for jd in job_dicts:
        job_id = str(jd.get("job_id"))
        
        # Skip if already processed in this batch
        if job_id in seen_in_batch:
            continue
        
        # Check if job already exists in DB
        if db.query(Job).filter_by(job_id=job_id).first():
            continue
        
        seen_in_batch.add(job_id)
        
        # Helper to safely serialize lists to JSON
        skills_json = json.dumps(jd.get("skills", []))
        tags_json = json.dumps(jd.get("tags", []))
        
        job = Job(
            job_id=job_id,
            title=safe_str(jd.get("title")),
            description=safe_str(jd.get("description")),
            company=safe_str(jd.get("company")),
            location=safe_str(jd.get("location")),
            url=safe_str(jd.get("url")),
            posted_date=safe_str(jd.get("posted_date")),
            category=safe_str(jd.get("category")),
            job_type=safe_str(jd.get("job_type")),
            experience_level=safe_str(jd.get("experience_level")),
            role_type=safe_str(jd.get("role_type")),
            skills=skills_json,
            tags=tags_json,
        )
        db.add(job)
        inserted += 1
    
    db.commit()
    return inserted

def get_all_jobs(db: Session) -> List[Job]:
    return db.query(Job).all()
