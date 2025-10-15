from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence

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


    def recommend_for_resume_text(self, resume_text: str, top_k: int = 5) -> List[Recommendation]:
        if not self._job_postings:
            raise RuntimeError("No job postings indexed")
        
        cleaned_resume = self.text_cleaner.clean(resume_text)
        
        resume_embedding = self.embedding_generator.encode([cleaned_resume])
        retrievals = self.vector_store.search(resume_embedding, k=top_k)[0]#perform similarity search
        resume_skills = self.skill_extractor.unique_skills(resume_text)
        return [self._build_recommendation(item, resume_skills) for item in retrievals]

    def recommend_for_resume_file(self, path: str | Path, top_k: int = 5) -> List[Recommendation]:
        parser = self.pdf_parser or PDFParser()
        text = parser.extract_text(path)
        return self.recommend_for_resume_text(text, top_k=top_k)

    def _build_recommendation(self, item: RetrievedItem, resume_skills: Iterable[str]) -> Recommendation:
        job = self._job_lookup(item.idx)
        # Use the pre-extracted skills from the job posting
        job_skills = set(job.skills)
        matched = sorted(job_skills.intersection(set(resume_skills)))
        return Recommendation(job=job, score=item.score, matched_skills=matched)

    def _job_lookup(self, vector_idx: int) -> JobPosting:
        job_id = self.vector_store.get_payload(vector_idx)
        for job in self._job_postings:
            if job.job_id == job_id:
                return job
        raise KeyError(f"Job id {job_id} missing from index")
