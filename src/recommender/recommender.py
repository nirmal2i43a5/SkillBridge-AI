from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence, Set

import logging
import numpy as np

from ..embeddings.text_embedder import TextEmbedder
from ..storage.vector_store import RetrievedItem, VectorStore
from ..ocr.pdf_parser import PDFParser
from ..preprocessing.skill_extractor import SkillExtractor
from ..preprocessing.text_cleaner import TextCleaner
from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


@dataclass
class JobPosting:
    """Represents a job posting with enriched metadata."""
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
    skills: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    min_years_experience: float = 0.0


@dataclass
class Recommendation:
    job: JobPosting
    score: float
    matched_skills: List[str]


class ResumeRecommender:
    def __init__(
        self,
        embedding_generator: TextEmbedder | None = None,
        vector_store: VectorStore | None = None,
        text_cleaner: TextCleaner | None = None,
        skill_extractor: SkillExtractor | None = None,
        pdf_parser: PDFParser | None = None,
    ) -> None:
        self.embedding_generator = embedding_generator or TextEmbedder()
        self.vector_store = vector_store or VectorStore()
        self.text_cleaner = text_cleaner or TextCleaner()
        self.skill_extractor = skill_extractor or SkillExtractor()
        self.pdf_parser = pdf_parser
        self._job_postings: List[JobPosting] = []

    def index_jobs(self, job_postings: Sequence[JobPosting]) -> None:
        self._job_postings = list(job_postings)
        cleaned = [self.text_cleaner.clean(job.description) for job in self._job_postings]
        embeddings = self.embedding_generator.encode(cleaned)
        payloads = [job.job_id for job in self._job_postings]
        self.vector_store.reset()
        self.vector_store.add_items(embeddings, payloads)
        logger.info("Indexed %d job postings", len(self._job_postings))

    def recommend_for_resume_text(
        self, 
        resume_text: str, 
        top_k: int = 5,
        resume_years_experience: float = 0.0
    ) -> List[Recommendation]:
        if not self._job_postings:
            raise RuntimeError("No job postings indexed")
        
        cleaned_resume = self.text_cleaner.clean(resume_text)
        
        resume_embedding = self.embedding_generator.encode([cleaned_resume])
        retrievals = self.vector_store.search(resume_embedding, k=top_k)[0]#perform similarity search
        resume_skills = self.skill_extractor.unique_skills(resume_text)
        
        return [
            self._build_recommendation(item, resume_skills, resume_years_experience) 
            for item in retrievals
        ]

    def recommend_for_resume_file(
        self, 
        path: str | Path, 
        top_k: int = 5,
        resume_years_experience: float = 0.0
    ) -> List[Recommendation]:
        parser = self.pdf_parser or PDFParser()
        text = parser.extract_text(path)
        return self.recommend_for_resume_text(text, top_k=top_k, resume_years_experience=resume_years_experience)

    def _build_recommendation(
        self, 
        item: RetrievedItem, 
        resume_skills: Iterable[str],
        resume_years: float
    ) -> Recommendation:
        job = self._job_lookup(item.idx)
        
        # 1. Semantic Score (Cosine Sim)
        semantic_score = item.score
        
        # 2. Skill Overlap Score (Jaccard)
        job_skills = set(job.skills) if job.skills else set(self.skill_extractor.unique_skills(job.description))
        resume_skills_set = set(resume_skills)
        matched_skills = sorted(job_skills.intersection(resume_skills_set))
        
        skill_score = 0.0
        if job_skills:
            skill_score = len(matched_skills) / len(job_skills)
            
        # 3. Experience Score
        exp_score = self._calculate_experience_score(resume_years, job.min_years_experience)
        
        # Hybrid Weighted Score
        # Weights: Semantic=0.6, Skills=0.2, Experience=0.2
        final_score = (0.6 * semantic_score) + (0.2 * skill_score) + (0.2 * exp_score)
        
        return Recommendation(job=job, score=final_score, matched_skills=matched_skills)

    def _calculate_experience_score(self, resume_years: float, job_min_years: float) -> float:
        if job_min_years <= 0:
            return 1.0 # No requirement
        
        if resume_years >= job_min_years:
            return 1.0
        elif resume_years >= (job_min_years * 0.5):
            return 0.5
        else:
            return 0.0

    def _job_lookup(self, vector_idx: int) -> JobPosting:
        job_id = self.vector_store.get_payload(vector_idx)
        for job in self._job_postings:
            if job.job_id == job_id:
                return job
        raise KeyError(f"Job id {job_id} missing from index")
