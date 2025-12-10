import json
import logging
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.preprocessing.experience_extractor import ExperienceExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enrich_jobs():
    data_path = Path("data/processed/adzuna_data_jobs.json")
    if not data_path.exists():
        logger.error(f"File not found: {data_path}")
        return

    logger.info(f"Loading jobs from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    extractor = ExperienceExtractor()
    enriched_count = 0
    
    logger.info("Extracting experience years...")
    for job in jobs:
        # Check if already has experience field to avoid overwriting if run multiple times (optional)
        # But we want to ensure it's populated, so we'll run it.
        
        description = job.get("job_description", "")
        years = extractor.extract_years(description)
        
        job["min_years_experience"] = years
        if years > 0:
            enriched_count += 1

    logger.info(f"Enriched {len(jobs)} jobs. Found experience for {enriched_count} jobs.")
    
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    logger.info("Saved enriched data.")

if __name__ == "__main__":
    enrich_jobs()
