
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence, Set
import re

@dataclass
class SkillMatch:
    skill: str
    occurrences: int


class SkillExtractor:
    """Improved skill extractor with fuzzy normalization and punctuation-tolerant matching."""

    def __init__(self, skills: Sequence[str] | None = None) -> None:
        base_skills = [s.strip().lower() for s in (skills or DEFAULT_SKILLS)]
        base_skills = list(dict.fromkeys(base_skills))  # deduplicate
        self._skills = {s.lower(): s for s in base_skills}
        self._pattern = self._build_pattern(base_skills)

    @staticmethod
    def _build_pattern(skills: Sequence[str]) -> re.Pattern[str]:
        """Build regex that tolerates punctuation, hyphens, and underscores."""
        escaped = sorted(skills, key=len, reverse=True)
        # Match multiword skills separated by optional punctuation/spaces
        pattern = r"(?<!\w)(" + "|".join(
            re.escape(skill).replace(r"\ ", r"[\s_\-/]+") for skill in escaped
        ) + r")(?!\w)"
        return re.compile(pattern, re.IGNORECASE)

    def _normalize_text(self, text: str) -> str:
        """Lowercase, remove excessive punctuation, normalize spaces."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s\+\#\-/]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract(self, text: str) -> List[SkillMatch]:
        
        """Extract skills from text (case-insensitive, punctuation-tolerant)."""
        normalized = self._normalize_text(text)
        counts: dict[str, int] = {}
        for match in self._pattern.findall(normalized):
            key = match.lower().strip()
            canonical = self._skills.get(key, key)
            counts[canonical] = counts.get(canonical, 0) + 1
        return [SkillMatch(skill=s, occurrences=c) for s, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]

    def unique_skills(self, text: str) -> Set[str]:
        return {m.skill for m in self.extract(text)}


DEFAULT_SKILLS: List[str] = [
    # --- Core Programming & Data Science ---
    "python", "r", "sql", "scala", "java", "julia", "sas", "matlab",
    "pandas", "numpy", "spark", "airflow", "hadoop",
    "tableau", "power bi", "looker", "databricks", "snowflake",
    "redshift", "bigquery", "mongodb",

    # --- Cloud & MLOps ---
    "aws", "azure", "gcp", "s3", "lambda", "emr", "sagemaker",
    "docker", "kubernetes", "terraform", "git", "jenkins", "ci/cd",
    "mlflow", "kubeflow", "dvc", "wandb", "model deployment", "model serving",

    # --- Machine Learning & Deep Learning ---
    "scikit-learn", "tensorflow", "pytorch", "keras", "xgboost", "lightgbm",
    "statistics", "regression", "classification", "clustering",
    "feature engineering", "eda", "data visualization", "time series forecasting",

    # --- NLP & Generative AI ---
    "machine learning", "deep learning", "nlp", "transformers",
    "bert", "roberta", "t5", "bloom", "gpt", "gpt-4", "gpt-3.5", "chatgpt",
    "mistral", "llama", "llama2", "llama3", "falcon", "gemma", "vicuna", "alpaca",
    "langchain", "llamaindex", "haystack", "huggingface", "sentence-transformers",
    "prompt engineering", "prompt tuning", "in-context learning",
    "retrieval augmented generation", "rag", "vector database",
    "chroma", "faiss", "pinecone", "weaviate", "milvus", "semantic search",
    "context window", "embedding models", "peft", "lora", "fine-tuning",

    # --- Vision & Multimodal AI ---
    "clip", "blip", "dalle", "stable diffusion", "image generation",
    "vision transformer", "ocr", "image captioning", "multimodal learning",

    # --- Audio & Speech ---
    "whisper", "text-to-speech", "speech recognition", "audio embeddings",

    # --- Deployment & APIs ---
    "fastapi", "flask", "streamlit", "gradio", "nginx", "vps",
    "api development", "backend development",

    # --- Responsible AI ---
    "responsible ai", "ethical ai", "bias detection", "explainable ai",
    "shap", "lime", "fairness in ai", "ai governance",

    # --- Advanced Topics ---
    "attention mechanism", "sequence modeling", "transformer models",
    "feature store", "data pipelines", "etl", "causal inference",
    "model quantization", "gpu inference", "model optimization"
]
