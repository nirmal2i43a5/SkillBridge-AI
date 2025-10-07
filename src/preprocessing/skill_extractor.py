from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Set

import re

@dataclass
class SkillMatch:
    skill: str
    occurrences: int


class SkillExtractor:
    """Rule-based skill extractor backed by a configurable vocabulary."""

    def __init__(self, skills: Sequence[str] | None = None) -> None:
        base_skills = skills or DEFAULT_SKILLS
        self._pattern = self._build_pattern(base_skills)
        self._skills = {skill.lower(): skill for skill in base_skills}

    @staticmethod
    def _build_pattern(skills: Sequence[str]) -> re.Pattern[str]:
        escaped = sorted(skills, key=len, reverse=True)
        pattern = r"\b(" + "|".join(re.escape(skill.lower()) for skill in escaped) + r")\b"
        return re.compile(pattern, re.IGNORECASE)

    def extract(self, text: str) -> List[SkillMatch]:
        counts: dict[str, int] = {}
        for match in self._pattern.findall(text.lower()):
            key = match.lower()
            canonical = self._skills.get(key, key)
            counts[canonical] = counts.get(canonical, 0) + 1
        return [SkillMatch(skill=s, occurrences=c) for s, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]

    def unique_skills(self, text: str) -> Set[str]:
        return {match.skill for match in self.extract(text)}


DEFAULT_SKILLS: List[str] = [
    "python",
    "java",
    "sql",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "pandas",
    "numpy",
    "scikit-learn",
    "pytorch",
    "tensorflow",
    "nlp",
    "machine learning",
    "deep learning",
    "data analysis",
    "data visualization",
    "fastapi",
    "streamlit",
    "faiss",
    "spark",
    "hadoop",
    "git",
]
