from __future__ import annotations
from pathlib import Path
import tempfile
import logging
from dataclasses import asdict
from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from src.backend.schemas import IndexJobsRequest, RecommendationRequest

from src.recommender.recommender import JobPosting, ResumeRecommender
from src.utils.logging_utils import setup_logging
from src.backend.services.indexer import index_jobs_from_payload
from datetime import datetime
from sqlalchemy.orm import Session
from src.backend.db import get_db
from src.backend.db.models import Resume
from src.ocr.pdf_parser import PDFParser

# Setup logging
logger = logging.getLogger(__name__)
setup_logging()

router = APIRouter()
recommender = ResumeRecommender()


# Endpoint: Index Job Postings
@router.post("/jobs/index")
async def index_jobs(payload: IndexJobsRequest) -> dict:
    if not payload.jobs:
        raise HTTPException(status_code=400, detail="No jobs provided")
    job_objects = [JobPosting(**job.model_dump()) for job in payload.jobs]
    recommender.index_jobs(job_objects)
    return {"indexed": len(job_objects)}




# Endpoint: Persist Jobs to DB
@router.post("/jobs/index/persist")
async def index_jobs_persist(payload: IndexJobsRequest, db: Session = Depends(get_db)) -> dict:
    inserted = index_jobs_from_payload(payload.model_dump(), db)
    return {"inserted": inserted}

# Endpoint: Recommend from Resume Text
@router.post("/recommend/text")
async def recommend_from_text(payload: RecommendationRequest) -> dict:
    if payload.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be positive")
    try:
        recs = recommender.recommend_for_resume_text(payload.resume_text, top_k=payload.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "recommendations": [
            asdict(rec.job) | {"score": rec.score, "matched_skills": rec.matched_skills}
            for rec in recs
        ]
    }

# Endpoint: Recommend from PDF Resume File
@router.post("/recommend/file")
async def recommend_from_file(upload: UploadFile = File(...), top_k: int = 5, db: Session = Depends(get_db)) -> dict:
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
        # Extract text
        parser = PDFParser()
        resume_text = parser.extract_text(tmp_path)

        # Save to DB
        db_resume = Resume(
            filename=upload.filename or "resume.pdf",
            content=resume_text,
            upload_date=datetime.utcnow()
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        recs = recommender.recommend_for_resume_text(resume_text, top_k=top_k)
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            logger.warning("Failed to clean up temp file %s", tmp_path)

    return {
        "recommendations": [
            {**asdict(rec.job), "score": rec.score, "matched_skills": rec.matched_skills}
            for rec in recs
        ]
    }
