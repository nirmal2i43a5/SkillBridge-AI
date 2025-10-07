from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional
import sys
import logging

repo_root = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd().parents[1]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))
    
from utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


@dataclass
class JobRecord:
    job_title: str
    job_description: str
    company: Optional[str]
    location: Optional[str]
    posted_date: Optional[str]
    source: str = "remoteok"
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    def to_serializable(self) -> dict:
        data = asdict(self)
        data["fetched_at"] = self.fetched_at.isoformat(timespec="seconds")
        return data

    @staticmethod
    def from_dict(data: dict) -> "JobRecord":
        fetched_at = data.get("fetched_at")
        return JobRecord(
            job_title=data.get("job_title", ""),
            job_description=data.get("job_description", ""),
            company=data.get("company"),
            location=data.get("location"),
            posted_date=data.get("posted_date"),
            source=data.get("source", "remoteok"),
            fetched_at=datetime.fromisoformat(fetched_at) if fetched_at else datetime.utcnow(),
        )


class JSONJobStore:
    """Lightweight JSON persistence for scraped job postings."""

    def __init__(self, json_path: str | Path = "data/processed/jobs.json") -> None:
        self.json_path = Path(json_path)
        self.json_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[JobRecord]:
        if not self.json_path.exists():
            return []
        try:
            payload = json.loads(self.json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse %s: %s", self.json_path, exc)
            return []
        return [JobRecord.from_dict(item) for item in payload]

    def persist(self, jobs: Iterable[JobRecord], deduplicate: bool = True) -> int:
        existing = self.load() if deduplicate else []
        existing_records = {self._record_key(job): job for job in existing}
        new_jobs = list(jobs)
        for job in new_jobs:
            existing_records[self._record_key(job)] = job
        serialized = [record.to_serializable() for record in existing_records.values()]
        serialized.sort(key=lambda item: item["fetched_at"], reverse=True)
        self.json_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
        logger.info("Persisted %d jobs to %s", len(new_jobs), self.json_path)
        return len(new_jobs)

    def recent(self, limit: int = 10) -> List[JobRecord]:
        records = self.load()
        records.sort(key=lambda job: job.fetched_at, reverse=True)
        return records[:limit]

    @staticmethod
    def _record_key(job: JobRecord) -> tuple:
        return (job.job_title.lower(), (job.company or "").lower(), (job.location or "").lower())
