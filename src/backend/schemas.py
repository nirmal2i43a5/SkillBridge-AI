from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class JobPostingBase(BaseModel):
    job_id: str
    title: str
    description: str
    company: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    posted_date: Optional[str] = None
    category: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    role_type: Optional[str] = None
    skills: List[str] = []
    tags: List[str] = []
    min_years_experience: float = 0.0

class JobPostingCreate(JobPostingBase):
    pass

class JobPosting(JobPostingBase):
    # Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)

class IndexJobsRequest(BaseModel):
    jobs: List[JobPostingCreate]

class RecommendationRequest(BaseModel):
    resume_text: str
    top_k: int = 5

class CandidateCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    raw_text: str
    skills: List[str] = []
    experience: List[dict] = []
    total_years_experience: float = 0.0

class CandidateResponse(CandidateCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
