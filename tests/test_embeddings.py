import numpy as np

from src.features.embedding_generator import EmbeddingGenerator


def test_embedding_generator_tfidf_shape():
    texts = [
        "machine learning with python",
        "deep learning with pytorch",
        "data analysis with pandas",
    ]
    generator = EmbeddingGenerator(prefer_tfidf=True)
    generator.fit_corpus(texts)
    embeddings = generator.encode(texts)
    assert embeddings.shape[0] == len(texts)
    assert embeddings.ndim == 2


def test_embedding_generator_consistency():
    corpus = ["python pandas", "docker kubernetes"]
    generator = EmbeddingGenerator(prefer_tfidf=True)
    generator.fit_corpus(corpus)
    first = generator.encode(["python pandas"])
    second = generator.encode(["python pandas"])
    assert np.allclose(first, second)
