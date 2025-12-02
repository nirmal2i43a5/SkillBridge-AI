from typing import List
from pydantic import BaseModel, Field

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

class ResumeBase(BaseModel):
    filename: str
    content: str
    upload_date: str

class ResumeCreate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int

    class Config:
        from_attributes = True
