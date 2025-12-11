import json
from typing import List, Any
from typing import List, Any
from .mongo_client import get_jobs_collection

def safe_str(val: Any) -> str | None:
    if val is None:
        return None
    if isinstance(val, list):
        return ", ".join(map(str, val))
    return str(val)


def add_jobs(job_dicts: List[dict]) -> int:
    collection = get_jobs_collection()
    inserted = 0
    
    # Bulk uypdate 
    for jd in job_dicts:
        job_id = str(jd.get("job_id"))
        
        # Prepare document
        doc = jd.copy()
        doc["job_id"] = job_id
        
        # Using job_id as unique key.
        result = collection.update_one(
            {"job_id": job_id}, 
            {"$set": doc}, 
            upsert=True
        )
        
        if result.upserted_id:
            inserted += 1
            
    return inserted


def get_all_jobs() -> List[dict]:
    collection = get_jobs_collection()
    return list(collection.find({}, {"_id": 0}))
