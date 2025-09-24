from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import requests

from ..storage.json_repository import JobRecord, JSONJobStore
from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()

API_URL = "https://remoteok.com/api"


@dataclass
class RemoteOKJob:
    job_title: str
    job_description: str
    company: Optional[str]
    location: Optional[str]
    posted_date: Optional[str]
    tags: List[str]
    job_url: Optional[str]


class RemoteOKClient:
    """Client for the RemoteOK job board API."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        output_path: str | Path = "data/processed/jobs.json",
        user_agent: str | None = None,
    ) -> None:
        self.session = session or requests.Session()
        if hasattr(self.session, "headers"):
            self.session.headers.setdefault(
                "User-Agent",
                user_agent or "ResumeMatcher/0.1 (+https://remoteok.com)"
            )
        self.store = JSONJobStore(output_path)

    def fetch_jobs(
        self,
        keyword: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
        persist: bool = True,
    ) -> List[RemoteOKJob]:
        payload = self._fetch_payload()
        tag_set = {tag.lower() for tag in tags or []}
        keyword_lower = keyword.lower() if keyword else None

        jobs: List[RemoteOKJob] = []
        for entry in payload:
            job = self._map_entry(entry)
            if job is None:
                continue
            if tag_set and not (tag_set & {t.lower() for t in job.tags}):
                continue
            if keyword_lower and keyword_lower not in job.job_title.lower() and keyword_lower not in job.job_description.lower():
                continue
            jobs.append(job)

        if persist and jobs:
            records = [
                JobRecord(
                    job_title=job.job_title,
                    job_description=job.job_description,
                    company=job.company,
                    location=job.location,
                    posted_date=job.posted_date,
                    source="remoteok",
                    fetched_at=datetime.utcnow(),
                )
                for job in jobs
            ]
            self.store.persist(records)
        logger.info("Collected %d jobs from RemoteOK", len(jobs))
        return jobs

    def _fetch_payload(self) -> List[dict]:
        resp = self.session.get(API_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            raise ValueError("Unexpected API response shape")
        return data

    @staticmethod
    def _map_entry(entry: dict) -> Optional[RemoteOKJob]:
        # RemoteOK returns a metadata header row with "legal" key; skip it.
        if not isinstance(entry, dict) or "position" not in entry:
            return None
        description = entry.get("description") or ""
        return RemoteOKJob(
            job_title=entry.get("position", ""),
            job_description=description,
            company=entry.get("company"),
            location=entry.get("location"),
            posted_date=entry.get("date"),
            tags=entry.get("tags", []) or [],
            job_url=entry.get("url"),
        )


def fetch_to_json(
    keyword: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    output_path: str | Path = "data/processed/jobs.json",
) -> int:
    client = RemoteOKClient(output_path=output_path)
    jobs = client.fetch_jobs(keyword=keyword, tags=tags, persist=True)
    return len(jobs)
