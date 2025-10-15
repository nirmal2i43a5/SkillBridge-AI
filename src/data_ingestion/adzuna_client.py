import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from src.preprocessing.skill_extractor import SkillExtractor
from src.preprocessing.text_cleaner import TextCleaner
from src.data_ingestion.schemas import AdzunaJob
from src.data_ingestion.tag_generator import DataJobTagGenerator
from src.data_ingestion.config import APP_ID, APP_KEY, BASE_URL, DATA_PROFESSIONAL_SKILLS



class AdzunaClient:
    def __init__(self, stopwords: Optional[List[str]] = None):
        self.session = requests.Session()
        self.text_cleaner = TextCleaner(stopwords)
        self.skill_extractor = SkillExtractor(DATA_PROFESSIONAL_SKILLS)
        self.tagger = DataJobTagGenerator(self.skill_extractor, self.text_cleaner)

    def fetch_full_description(self, url: str) -> str:
        if not url:
            return ""
        try:
            r = requests.get(url, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            return soup.get_text(separator=" ", strip=True)[:10000]
        except Exception:
            return ""

    def fetch_jobs(self, query: str, pages: int = 1, location: Optional[str] = None) -> List[AdzunaJob]:
        jobs: List[AdzunaJob] = []
        for page in range(1, pages + 1):
            url = f"{BASE_URL}{page}"
            params = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "results_per_page": 50,
                "what": query,
                "where": location or "",
            }
            r = self.session.get(url, params=params, timeout=30)
            if r.status_code != 200:
                print(f"HTTP {r.status_code} for {query} page {page}")
                break

            for entry in r.json().get("results", []):
                job = self._map_to_job(entry)
                if job:
                    skills, tags, role_type = self.tagger.generate_tags(job)
                    job.skills, job.tags, job.role_type = skills, tags, role_type
                    jobs.append(job)
        return jobs

    def _map_to_job(self, entry: dict) -> Optional[AdzunaJob]:
        if not isinstance(entry, dict):
            return None

        title = entry.get("title", "")
        description = entry.get("description", "") or ""
        company = entry.get("company", {}).get("display_name")
        location = entry.get("location", {}).get("display_name")
        category = entry.get("category", {}).get("label") if entry.get("category") else None
        url = entry.get("redirect_url")
        date = entry.get("created")

        # Fetch full description if truncated
        if description.endswith("…") or len(description) < 400:
            full_desc = self.fetch_full_description(url)
            # Try alternative URL format if first attempt fails
            if not full_desc and url and url.startswith("https://www.adzuna.ca/land"):
                alt_url = url.replace("/land/ad/", "/details/")
                full_desc = self.fetch_full_description(alt_url)
            
            if full_desc and len(full_desc) > len(description):
                print(f"  → Fetched full description for: {title[:50]}...")
                description = full_desc

        # Infer experience level from title
        title_lower = title.lower()
        if any(x in title_lower for x in ["lead", "principal", "staff"]):
            experience = "Lead/Principal"
        elif any(x in title_lower for x in ["senior", "sr"]):
            experience = "Senior"
        elif any(x in title_lower for x in ["junior", "jr", "entry"]):
            experience = "Junior"
        else:
            experience = None

        # Infer job type from description
        desc_lower = description.lower()
        if any(x in desc_lower for x in ["full time", "full-time", "permanent"]):
            job_type = "Full-time"
        elif "contract" in desc_lower:
            job_type = "Contract"
        elif "part time" in desc_lower:
            job_type = "Part-time"
        elif "intern" in title_lower:
            job_type = "Internship"
        else:
            job_type = None

        return AdzunaJob(
            job_title=title,
            job_description=description,
            company=company,
            location=location,
            category=category,
            job_type=job_type,
            experience_level=experience,
            posted_date=date,
            job_url=url,
        )
