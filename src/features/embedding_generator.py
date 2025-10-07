from __future__ import annotations

from typing import Iterable, List, Sequence

import logging
import numpy as np

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except ImportError:  # pragma: no cover
    SentenceTransformer = None  # type: ignore

from sklearn.feature_extraction.text import TfidfVectorizer

from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


class EmbeddingGenerator:
    """Text embedding helper supporting SBERT or TF-IDF fallback."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_tfidf_fallback: bool = True,
        prefer_tfidf: bool = False,
    ) -> None:
        self.model_name = model_name
        self.use_tfidf_fallback = use_tfidf_fallback
        self.prefer_tfidf = prefer_tfidf
        self._model = None if prefer_tfidf else self._load_model()
        self._tfidf: TfidfVectorizer | None = None

    def _load_model(self):
        if SentenceTransformer is None:
            if not self.use_tfidf_fallback:
                raise ImportError("sentence-transformers is not installed")
            logger.warning("SentenceTransformer unavailable; defaulting to TF-IDF embeddings")
            return None
        try:
            model = SentenceTransformer(self.model_name)
            logger.info("Loaded SentenceTransformer model %s", self.model_name)
            return model
        except Exception as exc:  # pragma: no cover - network issues
            if not self.use_tfidf_fallback:
                raise
            logger.warning("Falling back to TF-IDF embeddings: %s", exc)
            return None

    def fit_corpus(self, corpus: Sequence[str]) -> None:
        if self._model is None:
            self._tfidf = TfidfVectorizer(max_features=5000)
            self._tfidf.fit(corpus)

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        texts_list: List[str] = list(texts)
        if self._model is not None:
            embeddings = self._model.encode(texts_list, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.astype(np.float32)
        if self._tfidf is None:
            self.fit_corpus(texts_list)
        assert self._tfidf is not None
        embeddings = self._tfidf.transform(texts_list).astype(np.float32)
        return embeddings.toarray()
