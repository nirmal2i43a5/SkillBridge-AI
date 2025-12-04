from contextlib import asynccontextmanager
import json
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router, recommender
from .db import init_db, SessionLocal
from .db.repository import get_all_jobs
from src.recommender.recommender import JobPosting

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan_context(app: FastAPI):
    # Initialize DB
    init_db()
    
    # Load jobs from DB and index them
    db = SessionLocal()
    try:
        jobs = get_all_jobs(db)
        if jobs:
            job_objects = []
            for job in jobs:
                try:
                    skills = json.loads(job.skills) if job.skills else []
                    tags = json.loads(job.tags) if job.tags else []
                except json.JSONDecodeError:
                    skills = []
                    tags = []
                
                job_objects.append(JobPosting(
                    job_id=job.job_id,
                    title=job.title or "",
                    description=job.description or "",
                    company=job.company,
                    location=job.location,
                    url=job.url,
                    posted_date=job.posted_date,
                    category=job.category,
                    job_type=job.job_type,
                    experience_level=job.experience_level,
                    role_type=job.role_type,
                    skills=skills,
                    tags=tags
                ))
            recommender.index_jobs(job_objects)
            logger.info(f"Indexed {len(job_objects)} jobs from DB on startup.")
        else:
            logger.info("No jobs found in DB to index.")
    except Exception as e:
        logger.error(f"Error indexing jobs on startup: {e}")
    finally:
        db.close()
    yield

app = FastAPI(title="Resume Skill Matcher", version="0.1.0", lifespan=lifespan_context)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
        
app.include_router(router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
