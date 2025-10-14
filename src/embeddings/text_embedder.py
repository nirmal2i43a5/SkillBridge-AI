from __future__ import annotations

from typing import Iterable, List

import logging
import numpy as np

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except ImportError:  # pragma: no cover
    SentenceTransformer = None  # type: ignore

from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


class TextEmbedder:
    """Generates text embeddings using a Sentence-BERT model."""

    def __init__(self) -> None:
        """Initialize with the default Sentence-BERT model."""
        self._model_name = "multi-qa-MiniLM-L6-cos-v1"
        self._model = self._load_model()

    def _load_model(self) -> SentenceTransformer:
        """Load and return the Sentence-BERT model."""
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install it using: pip install sentence-transformers"
            )

        try:
            model = SentenceTransformer(self._model_name)
            logger.info("Loaded SentenceTransformer model: %s", self._model_name)
            return model
        except Exception as exc:
            logger.error("Error loading model %s: %s", self._model_name, exc)
            raise

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        """Convert input texts into normalized float32 embeddings."""
        texts_list: List[str] = list(texts)
        embeddings = self._model.encode(
            texts_list,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.astype(np.float32)
