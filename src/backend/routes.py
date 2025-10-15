from __future__ import annotations

from pathlib import Path
from typing import List
import logging
import tempfile
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from dataclasses import asdict
from ..recommender.recommender import JobPosting, ResumeRecommender
from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

router = APIRouter()
recommender = ResumeRecommender()


class JobPostingPayload(BaseModel):
    """Payload for indexing a job, now with all fields."""
    job_id: str
    title: str
    description: str
    company: str | None = None
    location: str | None = None
    url: str | None = None
    posted_date: str | None = None
    category: str | None = None
    job_type: str | None = None
    experience_level: str | None = None
    role_type: str | None = None
    skills: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


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
    return {"indexed": len(job_objects)}


@router.post("/recommend/text")
async def recommend_from_text(payload: RecommendationRequest) -> dict:
    if payload.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be positive")
    try:
        recs = recommender.recommend_for_resume_text(payload.resume_text, top_k=payload.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # Return all the new job fields in the response
    recommendation_results = {"recommendations": [rec.job.dict() | {"score": rec.score, "matched_skills": rec.matched_skills} for rec in recs]}
    return recommendation_results 


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
    # Return all the new job fields in the response
    recommendation_results = {
    "recommendations": [
        {**asdict(rec.job), "score": rec.score, "matched_skills": rec.matched_skills}
        for rec in recs
    ]
}
 
    return recommendation_results