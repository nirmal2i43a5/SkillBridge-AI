import re
from typing import List, Optional

class ExperienceExtractor:
    """Extracts years of experience from text using regex patterns."""

    def __init__(self):
        # Patterns to catch: "5 years experience", "5+ years", "2015-2020", "since 2018"
        self.year_patterns = [
            r"(\d+)\+?\s*years?",
            r"(\d+)\s*yrs?",
        ]
        self.date_range_pattern = r"(\d{4})\s*-\s*(Present|Current|\d{4})"
    
    def extract_years(self, text: str) -> float:
        """
        Estimate total years of experience. 
        This is a heuristic approach. 
        """
        # We take the maximum number mentioned near "experience" keywords
        lower_text = text.lower()
        max_years = 0.0
        
        # Look for explicit "X years of experience"
        matches = re.findall(r"(\d+)\+?\s*years?\s*of\s*experience", lower_text)
        if matches:
             years = [float(m) for m in matches if float(m) < 50] # Sanity check < 50
             if years:
                 return max(years)

        return 0.0
