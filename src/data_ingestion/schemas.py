from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class AdzunaJob:
    job_title: str
    job_description: str
    company: Optional[str]
    location: Optional[str]
    category: Optional[str]
    job_type: Optional[str]
    experience_level: Optional[str]
    posted_date: Optional[str]
    job_url: Optional[str]
    skills: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    role_type: Optional[str] = None
    source: str = "Adzuna"
