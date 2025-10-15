# Resume Skill Matcher

End-to-end system that parses resumes, extracts skills, generates embeddings, and recommends the most relevant job postings. The stack includes FastAPI for the backend, Streamlit for the frontend, FAISS/sklearn for vector search, and Sentence-BERT for embeddings.

## Features

- PDF parsing with pdfplumber/PyPDF2 fallback.
- Text cleaning and rule-based skill extraction.
- Embeddings via Sentence-BERT (multi-qa-MiniLM-L6-cos-v1), with FAISS or cosine neighbours for retrieval.
- FastAPI service exposing job indexing and recommendation endpoints.
- Streamlit UI for resume uploads and quick experimentation.
- Docker/Docker Compose setup for local orchestration.
- Reproducible scripts, notebooks, and tests.
- RemoteOK API ingestion pipeline persisting jobs into JSON for downstream use.
