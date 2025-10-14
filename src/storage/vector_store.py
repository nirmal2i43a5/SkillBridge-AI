from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import logging
import numpy as np
import faiss 




from ..utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


@dataclass
class RetrievedItem:
    idx: int
    score: float


class VectorStore:


    def __init__(self) -> None:
        self._index = None
        self._items: List[str] = []
        self._dim: int | None = None
        self._use_faiss = faiss is not None
        self._sk_embeddings: np.ndarray | None = None
        
        logger.info("VectorStore using FAISS backend")
       

    def reset(self) -> None:
        self._index = None
        self._items = []
        self._dim = None
        self._sk_embeddings = None

    def add_items(self, embeddings: np.ndarray, payloads: Sequence[str]) -> None:
        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be 2D array")
        if len(payloads) != embeddings.shape[0]:
            raise ValueError("Payload length mismatch")
        
        self._dim = embeddings.shape[1]
        self._items.extend(payloads)
        
        if self._use_faiss:
            self._add_with_faiss(embeddings)
        

    def _add_with_faiss(self, embeddings: np.ndarray) -> None:
        assert self._dim is not None
        if self._index is None:
            self._index = faiss.IndexFlatIP(self._dim)
        faiss.normalize_L2(embeddings)
        self._index.add(embeddings.astype(np.float32))

    # def _add_with_sklearn(self, embeddings: np.ndarray) -> None:
    #     new_embeddings = embeddings.astype(np.float32)
    #     if self._sk_embeddings is None:
    #         self._sk_embeddings = new_embeddings
    #     else:
    #         self._sk_embeddings = np.vstack([self._sk_embeddings, new_embeddings])
    #     if self._index is None:
    #         self._index = NearestNeighbors(metric="cosine")
    #     self._index.fit(self._sk_embeddings)

    def search(self, query_embeddings: np.ndarray, k: int = 5) -> List[List[RetrievedItem]]:
        if self._index is None:
            raise RuntimeError("Vector index is empty; call add_items first")
        if self._use_faiss:
            scores, indices = self._index.search(query_embeddings.astype(np.float32), k)
     
        return [
            [RetrievedItem(idx=int(idx), score=float(score)) for idx, score in zip(idx_row, score_row) if idx != -1]
            for idx_row, score_row in zip(indices, scores)
        ]

    def get_payload(self, idx: int) -> str:
        return self._items[idx]
