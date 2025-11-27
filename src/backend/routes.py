from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List

import logging
import tempfile
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ..recommender.recommender import JobPosting, ResumeRecommender
from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

router = APIRouter()
recommender = ResumeRecommender()
# Track last index time for status endpoint
recommender._last_index_time: datetime | None = None


class JobPostingPayload(BaseModel):
    job_id: str
    title: str
    description: str
    company: str | None = None
    location: str | None = None


class IndexJobsRequest(BaseModel):
    jobs: List[JobPostingPayload]


class RecommendationRequest(BaseModel):
    resume_text: str
    top_k: int = 5


@router.post("/jobs/index")
async def index_jobs(payload: IndexJobsRequest) -> dict:
    if not payload.jobs:
        raise HTTPException(status_code=400, detail="No jobs provided")
    job_objects = [JobPosting(**job.dict()) for job in payload.jobs]
    recommender.index_jobs(job_objects)
    # Track when indexing happened
    recommender._last_index_time = datetime.now(timezone.utc)
    return {"indexed": len(job_objects)}


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
            {
                "job_id": rec.job.job_id,
                "title": rec.job.title,
                "company": rec.job.company,
                "location": rec.job.location,
                "score": rec.score,
                "matched_skills": rec.matched_skills,
            }
            for rec in recs
        ]
    }


@router.post("/recommend/file")
async def recommend_from_file(upload: UploadFile = File(...), top_k: int = 5) -> dict:
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
        recs = recommender.recommend_for_resume_file(tmp_path, top_k=top_k)
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            logger.warning("Failed to clean up temp file %s", tmp_path)
    return {
        "recommendations": [
            {
                "job_id": rec.job.job_id,
                "title": rec.job.title,
                "company": rec.job.company,
                "location": rec.job.location,
                "score": rec.score,
                "matched_skills": rec.matched_skills,
            }
            for rec in recs
        ]
    }
