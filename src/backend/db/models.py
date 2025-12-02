from sqlalchemy import Column, Integer, String, Text, DateTime
from src.backend.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, unique=True, nullable=False)   # original ID from source
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    url = Column(String, nullable=True)
    posted_date = Column(String, nullable=True)
    category = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    role_type = Column(String, nullable=True)
    skills = Column(Text, nullable=True)  
    tags = Column(Text, nullable=True)

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Extracted text content
    upload_date = Column(DateTime, nullable=False)

