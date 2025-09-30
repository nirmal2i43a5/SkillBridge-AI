from __future__ import annotations

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
    return {"indexed": len(job_objects)}

