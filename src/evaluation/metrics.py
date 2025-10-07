from __future__ import annotations

from typing import Iterable, Sequence


def precision_at_k(recommended: Sequence[str], relevant: Sequence[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    top_k = recommended[:k]
    if not top_k:
        return 0.0
    rel_set = set(relevant)
    hits = sum(1 for item in top_k if item in rel_set)
    return hits / len(top_k)

def recall_at_k(recommended: Sequence[str], relevant: Sequence[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    rel_set = set(relevant)
    if not rel_set:
        return 0.0
    top_k = recommended[:k]
    hits = sum(1 for item in top_k if item in rel_set)
    return hits / len(rel_set)

def f1_at_k(recommended: Sequence[str], relevant: Sequence[str], k: int) -> float:
    precision = precision_at_k(recommended, relevant, k)
    recall = recall_at_k(recommended, relevant, k)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)

def mean_average_precision(recommendations: Sequence[Sequence[str]], relevants: Sequence[Iterable[str]]) -> float:
    if len(recommendations) != len(relevants):
        raise ValueError("Mismatched recommendation and relevance lengths")
    ap_scores = []
    for recs, rel in zip(recommendations, relevants):
        rel_set = set(rel)
        if not rel_set:
            ap_scores.append(0.0)
            continue
        hits = 0
        precision_sum = 0.0
        for idx, item in enumerate(recs, start=1):
            if item in rel_set:
                hits += 1
                precision_sum += hits / idx
        ap_scores.append(precision_sum / len(rel_set))
    return sum(ap_scores) / len(ap_scores) if ap_scores else 0.0
