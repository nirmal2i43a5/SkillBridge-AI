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
    "mlops engineer",
    "devops engineer",
    "software engineer",
    "ai engineer",
    "generative ai engineer",
    "analytics engineer",
    "bi developer",
    "business intelligence developer",
    "research scientist",
]

DATA_PROFESSIONAL_SKILLS = [
    # --- Software Engineering: Languages ---
    "python", "javascript", "typescript", "java", "c++", "c", "c#", "go", "golang", "rust",
    "swift", "kotlin", "ruby", "php", "scala", "julia", "lua", "shell", "bash",

    # --- Software Engineering: Web & Backend ---
    "react", "angular", "vue", "next.js", "node.js", "express", "nestjs",
    "django", "flask", "fastapi", "spring boot", "asp.net", ".net", "ruby on rails",
    "graphql", "rest api", "grpc", "microservices", "serverless", "event-driven",

    # --- Software Engineering: DevOps & Cloud ---
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "gitlab ci", "circleci", "prometheus", "grafana",
    "linux", "unix", "sre", "site reliability engineering",

    # --- Data Engineering & Databases ---
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
    "dynamodb", "snowflake", "databricks", "bigquery", "redshift",
    "spark", "pyspark", "hadoop", "kafka", "flink", "airflow", "trino", "presto", "dbt",
    "etl", "elt", "data pipeline", "data warehousing", "data governance",

    # --- Data Science & MLE ---
    "pandas", "numpy", "scikit-learn", "scipy", "statsmodels",
    "tensorflow", "pytorch", "keras", "xgboost", "lightgbm", "catboost",
    "mlflow", "kubeflow", "wandb", "dvc", "mlops", "model serving",
    "a/b testing", "causal inference", "statistics", "mathematics",

    # --- Generative AI: LLMs & Models ---
    "llm", "large language model", "gpt-4", "gpt-3.5", "claude", "gemini",
    "llama", "mistral", "mixtral", "falcon", "gemma", "stable diffusion",
    "midjourney", "dalle", "clip", "whisper", "transformers", "bert",

    # --- Generative AI: Techniques ---
    "rag", "retrieval augmented generation", "prompt engineering", "chain of thought",
    "fine-tuning", "peft", "lora", "qlora", "rlhf", "dpo", "quantization",
    "vector database", "pinecone", "chroma", "weaviate", "milvus", "qdrant",
    "langchain", "llamaindex", "semantic search", "embeddings",

    # --- Agentic AI & Autonomous Systems ---
    "autonomous agents", "agentic ai", "multi-agent systems", "autogen",
    "crewai", "langgraph", "babyagi", "autogpt", "chatdev",
    "react pattern", "planning", "tool use", "function calling",

    # --- Domain Specific: Finance/Web3 ---
    "web3", "defi", "crypto", "blockchain", "smart contracts", "solidity",
    "quantitative finance", "financial modeling", "algorithmic trading",
    "risk management", "fraud detection",

    # --- Soft Skills & Methodologies ---
    "agile", "scrum", "kanban", "jira", "confluence",
    "problem solving", "communication", "leadership", "mentoring",
]