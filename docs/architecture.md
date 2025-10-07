# System Architecture

## Overview
The Resume Skill Matcher consists of four primary layers working together:

1. **Data ingestion** - Handles resume PDF parsing, RemoteOK API ingestion, and job posting ingestion.
2. **Preprocessing** - Cleans text, extracts skills, and prepares structured documents.
3. **Embedding + Retrieval** - Generates vector embeddings and performs similarity search with FAISS/sklearn.
4. **Application surfaces** - Exposes REST APIs (FastAPI) and an interactive frontend (Streamlit).

## Data Flow
1. Resumes arrive as PDF uploads or plain text.
2. `PDFParser` extracts raw text, `TextCleaner` normalizes it, and `SkillExtractor` derives domain skills.
3. `EmbeddingGenerator` produces embeddings; `VectorStore` persists vectors and enables nearest-neighbour search.
4. `ResumeRecommender` orchestrates matching and returns ranked job recommendations.
5. Backend APIs and the Streamlit client consume the recommender for end-user interaction.

## Components
- **OCR**: `src/ocr/pdf_parser.py` with pdfplumber/PyPDF2 fallback.
- **Scraper**: `src/data_collection/arbeitnow_api.py` harvests RemoteOK job listings into JSON for downstream use.
- **Preprocessing**: Tokenization, stopword removal, skill extraction.
- **Feature Store**: FAISS index for dense retrieval with TF-IDF fallback when GPU/backends are unavailable.
- **Backend**: FastAPI app (`src/backend`) exposing endpoints for job indexing and recommendations.
- **Frontend**: Streamlit UI (`src/frontend/app.py`) enabling quick uploads and index management.
- **Evaluation**: Metrics in `src/evaluation/metrics.py` and companion notebooks for offline experiments.

## Deployment
- **Local**: `docker-compose.yaml` runs backend and frontend services.
- **Production**: Build and push Docker images; provision a vector database or managed FAISS service as needed.
- **Monitoring**: Integrate structured logging via `logging_utils.setup_logging` and add metrics exporters (future work).

## Future Enhancements
- Swap rule-based skill extraction with spaCy or transformer-based NER.
- Introduce persistent storage for embeddings (e.g., Chroma or pgvector).
- Add authentication and multi-tenant separation in the API.
- Expand evaluation suite with real-world labelled datasets and A/B testing hooks.
