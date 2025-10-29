import numpy as np
import pytest

from src.embeddings.text_embedder import TextEmbedder


def test_embedding_generator_shape():
    """Test that embeddings have correct shape."""
    texts = [
        "machine learning with python",
        "deep learning with pytorch",
        "data analysis with pandas",
    ]
    generator = TextEmbedder()
    embeddings = generator.encode(texts)
    assert embeddings.shape[0] == len(texts)
    assert embeddings.ndim == 2
    assert embeddings.dtype == np.float32


def test_embedding_generator_consistency():
    """Test that same text produces same embeddings."""
    generator = TextEmbedder()
    first = generator.encode(["python pandas"])
    second = generator.encode(["python pandas"])
    assert np.allclose(first, second)


def test_embedding_generator_normalized():
    """Test that embeddings are L2-normalized."""
    texts = ["data science", "machine learning"]
    generator = TextEmbedder()
    embeddings = generator.encode(texts)
    
    # Check that L2 norms are approximately 1
    norms = np.linalg.norm(embeddings, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)


def test_embedding_generator_different_texts():
    """Test that different texts produce different embeddings."""
    generator = TextEmbedder()
    embeddings = generator.encode(["python programming", "java development"])
    
    # Ensure embeddings are different
    assert not np.allclose(embeddings[0], embeddings[1])


def test_embedding_generator_custom_model():
    """Test initialization with custom model name."""
    generator = TextEmbedder()
    assert generator._model_name == "multi-qa-MiniLM-L6-cos-v1"
    
    # Test it can encode
    embeddings = generator.encode(["test text"])
    assert embeddings.shape[0] == 1
