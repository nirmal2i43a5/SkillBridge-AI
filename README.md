# Resume Skill Matcher

End-to-end system that parses resumes, extracts skills, generates embeddings, and recommends the most relevant job postings. The stack includes FastAPI for the backend, Streamlit for the frontend, FAISS/sklearn for vector search, and Sentence-BERT (with TF-IDF fallback) for embeddings.

## Features
- PDF parsing with pdfplumber/PyPDF2 fallback.
- Text cleaning and rule-based skill extraction.
- Embeddings via Sentence-BERT or TF-IDF fallback, with FAISS or cosine neighbours for retrieval.
- FastAPI service exposing job indexing and recommendation endpoints.
- Streamlit UI for resume uploads and quick experimentation.
- Docker/Docker Compose setup for local orchestration.
- Reproducible scripts, notebooks, and tests.
- RemoteOK API ingestion pipeline persisting jobs into JSON for downstream use.

## Getting Started
`ash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
`

## Fetching Jobs
`ash
python scripts/scrape_jobs.py --keyword "python" --tag data --tag machine-learning
`
Jobs are persisted to data/processed/jobs.json and can be loaded into the recommender pipeline.

## Indexing & Recommendations
`ash
python scripts/run_pipeline.py examples/resume.txt src/frontend/sample_jobs.json
`

## Run Services Locally
`ash
docker compose up --build
`

## Project Layout
`
skillmatch/
+-- src/                # Core application code
+-- scripts/            # Helper CLI entrypoints
+-- tests/              # Pytest-based unit tests
+-- notebooks/          # Exploratory analysis
+-- docs/               # Architecture and evaluation docs
+-- data/               # Raw/processed datasets and embeddings
`

## Configuration
- Set SKILLMATCH_API_URL for the Streamlit frontend when remote.
- Modify src/preprocessing/skill_extractor.py to extend the skill vocabulary.
- Provide production-grade credentials/secrets via environment variables or .env files (not committed).

## Testing
`ash
python -m pytest
`

## Contributing
Please see CONTRIBUTING.md for contribution guidelines.
