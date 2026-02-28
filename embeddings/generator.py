"""
HemaV MedAssist — Embedding Generation

Uses Sentence Transformers (all-MiniLM-L6-v2) to generate 384-dimensional
dense vector embeddings for medical text.

Why this model:
- 384 dimensions: good balance of quality vs. storage/speed
- Trained on 1B+ sentence pairs for semantic similarity
- Fast inference (~14K sentences/sec on GPU)
- Ideal for cosine similarity search
"""
import logging
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

logger = logging.getLogger("hemav.embeddings")

_model = None  # Lazy-loaded singleton


def get_model() -> SentenceTransformer:
    """Load the embedding model (cached singleton)."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"Model loaded — dimension={_model.get_sentence_embedding_dimension()}")
    return _model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings.tolist()


def generate_single_embedding(text: str) -> list[float]:
    """Generate embedding for a single text query."""
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()
