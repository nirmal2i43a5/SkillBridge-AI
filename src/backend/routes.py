from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Any
import logging
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from .db.mongo_client import get_candidates_collection
from .schemas import IndexJobsRequest, RecommendationRequest, CandidateResponse, JobPosting
from .services.indexer import index_jobs_from_payload
from ..recommender.recommender import ResumeRecommender, JobPosting as RecommenderJob
from ..utils.logging_utils import setup_logging
from ..ocr.pdf_parser import PDFParser
from ..preprocessing.experience_extractor import ExperienceExtractor

# Setup logging
logger = logging.getLogger(__name__)
setup_logging()

router = APIRouter()
recommender = ResumeRecommender()
experience_extractor = ExperienceExtractor()

# Track last index time for status endpoint
recommender._last_index_time: datetime | None = None

@router.post("/jobs/index")
async def index_jobs(payload: IndexJobsRequest) -> dict:
    if not payload.jobs:
        raise HTTPException(status_code=400, detail="No jobs provided")
    
    # Index in FAISS/Recommender
    # Map Pydantic JobPosting to RecommenderJob
    job_objects = []
    seen_ids = set()

    for job in payload.jobs:
        if job.job_id in seen_ids:
            continue
        seen_ids.add(job.job_id)

        rec_job = RecommenderJob(
            job_id=job.job_id,
            title=job.title,
            description=job.description,
            company=job.company,
            location=job.location,
            url=job.url,
            posted_date=job.posted_date,
            category=job.category,
            job_type=job.job_type,
            experience_level=job.experience_level,
            role_type=job.role_type,
            skills=job.skills,
            tags=job.tags,
            min_years_experience=job.min_years_experience
        )
        job_objects.append(rec_job)
        
        # 2. Persist to DB (MongoDB)
        # Note: We rely on the services/indexer.py which delegates to repository.py
        
    
    # Mongo Logic via Helper
    index_jobs_from_payload(payload.model_dump())
    
    recommender.index_jobs(job_objects)
    recommender._last_index_time = datetime.now(timezone.utc)
    
    return {"indexed": len(job_objects), "persisted": True}




# Endpoint: Persist Jobs to DB
@router.post("/jobs/index/persist")
async def index_jobs_persist(payload: IndexJobsRequest) -> dict:
    inserted = index_jobs_from_payload(payload.model_dump())
    return {"inserted": inserted}

# Endpoint: Recommend from Resume Text
@router.post("/recommend/text")
async def recommend_from_text(
    payload: RecommendationRequest
) -> dict:
    if payload.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be positive")
    
    candidate_id = "mongo_id" # Placeholder
    try:
        # 1. Extract Years of Experience
        years_exp = experience_extractor.extract_years(payload.resume_text)
        
        # 2. Save Candidate to DB
        # MongoDB Implementation
        candidates_col = get_candidates_collection()
        candidate_doc = {
            "raw_text": payload.resume_text,
            "total_years_experience": years_exp,
            "upload_date": datetime.now(timezone.utc)
        }
        result = candidates_col.insert_one(candidate_doc)
        candidate_id = str(result.inserted_id)

        # 3. Get Recommendations
        recs = recommender.recommend_for_resume_text(
            payload.resume_text, 
            top_k=payload.top_k, 
            resume_years_experience=years_exp
        )
        
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
        
    return {
        "candidate_id": candidate_id,
        "detected_years_experience": years_exp,
        "recommendations": [
            {
                "job_id": rec.job.job_id,
                "title": rec.job.title,
                "company": rec.job.company,
                "location": rec.job.location,
                "score": rec.score,
                "matched_skills": rec.matched_skills,
                "min_years_experience": rec.job.min_years_experience,
                "skills": rec.job.skills,
                "job_type": rec.job.job_type,
                "experience_level": rec.job.experience_level,
                "role_type": rec.job.role_type,
                "url": rec.job.url
            }
            for rec in recs
        ]
    }

#  Recommend from PDF Resume File
@router.post("/recommend/file")
async def recommend_from_file(
    upload: UploadFile = File(...), 
    top_k: int = 5
) -> dict:
    if top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be positive")


    suffix = Path(upload.filename or "resume").suffix.lower()
    if suffix != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF resumes supported")


    contents = await upload.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)


    candidate_id = "mongo_id"
    try:
        # Extract Text
        parser = PDFParser()
        resume_text = parser.extract_text(tmp_path)
        
        # Extract Experience
        years_exp = experience_extractor.extract_years(resume_text)

        #  Save to DB
        candidates_col = get_candidates_collection()
        candidate_doc = {
            "name": upload.filename,
            "raw_text": resume_text,
            "total_years_experience": years_exp,
            "upload_date": datetime.now(timezone.utc)
        }
        result = candidates_col.insert_one(candidate_doc)
        candidate_id = str(result.inserted_id)
        
        # 4. Recommend
        recs = recommender.recommend_for_resume_text(
            resume_text, 
            top_k=top_k,
            resume_years_experience=years_exp
        )
        
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            logger.warning("Failed to clean up temp file %s", tmp_path)


    return {
        "candidate_id": candidate_id,
        "detected_years_experience": years_exp,
        "recommendations": [
            {
                "job_id": rec.job.job_id,
                "title": rec.job.title,
                "company": rec.job.company,
                "location": rec.job.location,
                "score": rec.score,
                "matched_skills": rec.matched_skills,
                "min_years_experience": rec.job.min_years_experience,
                "skills": rec.job.skills,
                "job_type": rec.job.job_type,
                "experience_level": rec.job.experience_level,
                "role_type": rec.job.role_type,
                "url": rec.job.url
            }
            for rec in recs
        ]
    }
