import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")
COUNTRY = "ca"
BASE_URL = os.getenv("BASE_URL", f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/")


DATA_ROLE_QUERIES = [
    "data scientist",
    "data engineer",
    "data analyst",
    "machine learning engineer",
    "ml engineer",
    "data architect",
    "analytics engineer",
    "bi developer",
    "business intelligence developer",
    "research scientist",
]

DATA_PROFESSIONAL_SKILLS = [
    # --- Core Programming & DS ---
    "python", "r", "sql", "scala", "java", "julia", "sas", "matlab",
    "pandas", "numpy", "spark", "airflow", "hadoop", "tableau", "power bi",
    "looker", "databricks", "snowflake", "redshift", "bigquery", "mongodb",

    # --- Cloud & MLOps ---
    "aws", "azure", "gcp", "s3", "lambda", "emr", "sagemaker",
    "docker", "kubernetes", "terraform", "git", "jenkins", "ci/cd",
    "mlflow", "kubeflow", "dvc", "wandb", "model deployment", "model serving",

    # --- Machine Learning & Deep Learning ---
    "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm",
    "statistics", "regression", "clustering", "classification",
    "feature engineering", "data visualization", "eda", "time series forecasting",

    # --- NLP & Generative AI ---
    "machine learning", "deep learning", "nlp", "transformers",
    "bert", "roberta", "t5", "bloom", "gpt", "gpt-4", "gpt-3.5", "chatgpt",
    "mistral", "llama", "llama2", "llama3", "falcon", "gemma", "vicuna", "alpaca",
    "langchain", "llamaindex", "haystack", "huggingface", "sentence-transformers",
    "prompt engineering", "prompt tuning", "in-context learning",
    "retrieval augmented generation", "rag", "vector database", "chroma",
    "faiss", "pinecone", "weaviate", "milvus", "semantic search",

    # --- Vision & Multimodal AI ---
    "clip", "blip", "dalle", "stable diffusion", "image generation",
    "vision transformer", "ocr", "image captioning",

    # --- Audio & Speech ---
    "whisper", "text-to-speech", "speech recognition", "audio embeddings",

    # --- Deployment Frameworks ---
    "fastapi", "flask", "streamlit", "gradio", "nginx", "vps",
    "api development", "backend development",

    # --- Responsible AI ---
    "responsible ai", "ethical ai", "bias detection", "explainable ai",
    "shap", "lime", "fairness in ai", "ai governance",

    # --- Advanced Topics ---
    "transformer models", "attention mechanism", "sequence modeling",
    "context window", "embedding models", "model fine-tuning", "lora", "peft",
]