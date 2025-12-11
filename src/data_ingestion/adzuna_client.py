
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.preprocessing.skill_extractor import SkillExtractor
from src.preprocessing.text_cleaner import TextCleaner
from src.data_ingestion.schemas import AdzunaJob
from src.data_ingestion.tag_generator import DataJobTagGenerator
from src.data_ingestion.config import APP_ID, APP_KEY, BASE_URL, DATA_PROFESSIONAL_SKILLS


class AdzunaClient:
    def __init__(self, stopwords: Optional[List[str]] = None):
        # Safe request session
        self.session = requests.Session()
        # # Use a real browser User-Agent to avoid 403 Forbidden
        # self.session.headers.update({
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        # })

        retries = Retry(
            total=5,                    
            backoff_factor=1,      
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.text_cleaner = TextCleaner(stopwords)
        self.skill_extractor = SkillExtractor(DATA_PROFESSIONAL_SKILLS)
        self.tagger = DataJobTagGenerator(self.skill_extractor, self.text_cleaner)


    def fetch_full_description(self, url: str) -> str:
        if not url:
            return ""

        try:
            r = self.session.get(url, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            return soup.get_text(separator=" ", strip=True)[:10000]
        except Exception as e:
            print(f"[WARN] full description fetch failed: {e}")
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

            try:
                r = self.session.get(url, params=params, timeout=30)
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] API request failed (page {page}): {e}")
                time.sleep(2)
                continue

    
            if r.status_code != 200:
                print(f"[WARN] HTTP {r.status_code} for {query} page {page}")
                if r.status_code == 429:
                    print(" → Rate limit hit. Sleeping 5 seconds...")
                    time.sleep(5)
                    continue
                break

            # Parse results
            results = r.json().get("results", [])
            for entry in results:
                job = self._map_to_job(entry)
                if job:
                    # Extract skills & tags & experience
                    skills, tags, role_type, min_years = self.tagger.generate_tags(job)
                    job.skills = skills
                    job.tags = tags
                    job.role_type = role_type
                    job.min_years_experience = min_years
                    jobs.append(job)

        return jobs

    #map api response to job desc 
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

            # Try alternative Adzuna URL
            if not full_desc and url and url.startswith("https://www.adzuna.ca/land"):
                alt_url = url.replace("/land/ad/", "/details/")
                full_desc = self.fetch_full_description(alt_url)

            if full_desc and len(full_desc) > len(description):
                print(f" Full description fetched for: {title[:50]}...")
                description = full_desc

        # Infer experience level
        title_lower = title.lower()
        if any(x in title_lower for x in ["lead", "principal", "staff"]):
            experience = "Lead/Principal"
        elif any(x in title_lower for x in ["senior", "sr"]):
            experience = "Senior"
        elif any(x in title_lower for x in ["junior", "jr", "entry"]):
            experience = "Junior"
        else:
            experience = None

        # Infer job type
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
            job_id=str(entry.get("id", "")),
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
