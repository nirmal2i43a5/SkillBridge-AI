from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    # Storing complex types as JSON for SQLite simplicity
    skills = Column(JSON, default=list) 
    experience = Column(JSON, default=list)
    total_years_experience = Column(Float, default=0.0)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # We could store embedding as a BLOB or JSON
    # embedding = Column(JSON, nullable=True)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    company = Column(String, index=True)
    location = Column(String, index=True)
    url = Column(String, nullable=True)
    min_years_experience = Column(Float, default=0.0)
    
    skills = Column(JSON, default=list)
    # embedding = Column(JSON, nullable=True)
