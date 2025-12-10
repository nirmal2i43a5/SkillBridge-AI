from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List
import logging
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from sqlalchemy.orm import Session

# Local imports
from .db import get_db
from .db.models import Candidate, Job
from .schemas import IndexJobsRequest, RecommendationRequest, CandidateResponse, JobPosting
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
async def index_jobs(payload: IndexJobsRequest, db: Session = Depends(get_db)) -> dict:
    if not payload.jobs:
        raise HTTPException(status_code=400, detail="No jobs provided")
    
    # 1. Index in FAISS/Recommender
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
        
        # 2. Persist to DB (SQLite) - Simple upsert
        existing_job = db.query(Job).filter(Job.job_id == job.job_id).first()
        if not existing_job:
            db_job = Job(
                job_id=job.job_id,
                title=job.title,
                description=job.description,
                company=job.company,
                location=job.location,
                url=job.url,
                min_years_experience=job.min_years_experience,
                skills=job.skills
            )
            db.add(db_job)
    
    db.commit()
    
    recommender.index_jobs(job_objects)
    recommender._last_index_time = datetime.now(timezone.utc)
    
    return {"indexed": len(job_objects), "persisted": True}


@router.post("/recommend/text")
async def recommend_from_text(
    payload: RecommendationRequest, 
    db: Session = Depends(get_db)
) -> dict:
    if payload.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be positive")
    
    try:
        # 1. Extract Years of Experience
        years_exp = experience_extractor.extract_years(payload.resume_text)
        
        # 2. Save Candidate to DB
        candidate = Candidate(
            raw_text=payload.resume_text,
            total_years_experience=years_exp,
            upload_date=datetime.now(timezone.utc)
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        # 3. Get Recommendations
        recs = recommender.recommend_for_resume_text(
            payload.resume_text, 
            top_k=payload.top_k, 
            resume_years_experience=years_exp
        )
        
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
        
    return {
        "candidate_id": candidate.id,
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


@router.post("/recommend/file")
async def recommend_from_file(
    upload: UploadFile = File(...), 
    top_k: int = 5,
    db: Session = Depends(get_db)
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

    try:
        # 1. Extract Text
        parser = PDFParser()
        resume_text = parser.extract_text(tmp_path)
        
        # 2. Extract Experience
        years_exp = experience_extractor.extract_years(resume_text)

        # 3. Save to DB
        candidate = Candidate(
            name=upload.filename, # Simple fallback
            raw_text=resume_text,
            total_years_experience=years_exp,
            upload_date=datetime.now(timezone.utc)
        )
        db.add(candidate)
        db.commit()
        
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
        "candidate_id": candidate.id,
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
