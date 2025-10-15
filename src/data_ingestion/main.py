import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from src.data_ingestion.adzuna_client import AdzunaClient
from src.data_ingestion.config import DATA_ROLE_QUERIES
from src.data_ingestion.schemas import AdzunaJob
from src.data_ingestion.utils import print_statistics

def fetch_all_data_jobs(
    pages_per_role: int = 5,
    output_path: str = "data/processed/adzuna_jobs_test.json",
    location: str = "Canada",
    stopwords: Optional[List[str]] = None,
):
    
    """ pipeline work flow: fetch -> clean -> save -> print summary."""
    
    client = AdzunaClient(stopwords)
    all_jobs: List[AdzunaJob] = []

    for role in DATA_ROLE_QUERIES:
        print(f"Fetching jobs for: {role}")
        jobs = client.fetch_jobs(role, pages=pages_per_role, location=location)
        all_jobs.extend(jobs)
        print(f"  Collected {len(jobs)} jobs for {role}")

    # Save to JSON
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            [j.__dict__ | {"fetched_at": datetime.utcnow().isoformat()} for j in all_jobs],
            f, ensure_ascii=False, indent=2
        )

    print(f"\nSaved {len(all_jobs)} jobs to {output_path}")
    print_statistics(all_jobs)

if __name__ == "__main__":
    fetch_all_data_jobs()
