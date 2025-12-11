# src/data_ingestion/tag_generator.py
from typing import List, Optional, Set
from src.preprocessing.skill_extractor import SkillExtractor
from src.preprocessing.text_cleaner import TextCleaner
from src.data_ingestion.config import DATA_ROLE_QUERIES
from src.data_ingestion.schemas import AdzunaJob

class DataJobTagGenerator:
    def __init__(self, skill_extractor: SkillExtractor, text_cleaner: TextCleaner):
        self.skill_extractor = skill_extractor
        self.text_cleaner = text_cleaner

    def generate_tags(self, job: AdzunaJob):
        """Extract skills, detect role type, and find tags like remote/hybrid."""
        text = f"{job.job_title}. {job.job_description or ''}"
        
        # Extract skills from the ORIGINAL text BEFORE cleaning
        # This preserves special characters in skill names (e.g., C++, C#)
        matches = self.skill_extractor.extract(text)
        skills = sorted({m.skill.lower() for m in matches}) if matches else []
        
        # Clean text for tag detection
        cleaned_text = self.text_cleaner.clean(text)

        # Identify job role
        role_type = next((r.title() for r in DATA_ROLE_QUERIES if r in job.job_title.lower()), None)

        # Create or extract tags (location, type, ...)
        tags: Set[str] = set()
        if job.location: tags.update(job.location.split(","))
        if job.job_type: tags.add(job.job_type)
        if job.experience_level: tags.add(job.experience_level)
        for env in ["remote", "hybrid", "onsite", "flexible"]:
            if env in cleaned_text.lower():
                tags.add(env)

        # Extract numeric experience
        min_years = 0.0
        # Match "5 years", "3+ years", "5-7 years"
        # We take the *minimum* found if a range, or the specific number.
        import re
        # Regex to find digit(s) followed by 'year' or 'yrs'
        # Handles: "5 years", "5+ years", "5-7 years" (takes 5), "minimum 3 years"
        exp_match = re.search(r'(\d+)(?:\s*[-–]\s*\d+)?\s*\+?\s*(?:year|yr)s?', cleaned_text.lower())
        if exp_match:
            try:
                min_years = float(exp_match.group(1))
            except ValueError:
                pass

        return skills, sorted(tags), role_type, min_years
