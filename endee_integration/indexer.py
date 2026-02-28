"""
HemaV MedAssist — Endee Vector DB: Index Manager

Handles creating the HNSW index in Endee and batch upserting
document embeddings with metadata for source attribution.

Why Endee (Vector DB) instead of SQL:
- SQL uses exact matching (WHERE clause) — can't find semantically similar text
- Vector DB uses ANN (Approximate Nearest Neighbor) search with HNSW algorithm
- Cosine similarity captures meaning: "tired" ≈ "fatigue" ≈ "exhaustion"
- Sub-millisecond search even with millions of vectors
- Metadata + filter support for structured retrieval

Why Cosine Similarity:
- Measures angle between vectors, not magnitude
- Normalizes for document length (short vs long chunks)
- Industry standard for text embeddings (Sentence Transformers trained on cosine)
- Range [0, 1] makes confidence scores interpretable
"""
import logging
from endee import Endee, Precision
from config import ENDEE_HOST, ENDEE_AUTH_TOKEN, INDEX_NAME, EMBEDDING_DIMENSION

logger = logging.getLogger("hemav.endee.indexer")


def get_client() -> Endee:
    """Initialize the Endee client."""
    if ENDEE_AUTH_TOKEN:
        client = Endee(ENDEE_AUTH_TOKEN)
    else:
        client = Endee()
    client.set_base_url(f"{ENDEE_HOST}/api/v1")
    return client


def create_index(client: Endee = None):
    """Create the medical docs index in Endee if it doesn't exist."""
    if client is None:
        client = get_client()

    try:
        # Try to get the index. If it exists, this succeeds.
        client.get_index(name=INDEX_NAME)
        logger.info(f"Index '{INDEX_NAME}' already exists — skipping creation")
        return
    except Exception:
        # If it doesn't exist, we create it
        pass

    try:
        client.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            space_type="cosine",           # Cosine similarity for semantic matching
            precision=Precision.FLOAT16,   # 16-bit precision: good accuracy, half the memory
        )
        logger.info(f"Created Endee index '{INDEX_NAME}' (dim={EMBEDDING_DIMENSION}, cosine, FLOAT16)")
    except Exception as e:
        if "already exists" in str(e).lower() or "Conflict" in str(e):
            logger.info(f"Index '{INDEX_NAME}' already exists — skipping creation")
        else:
            raise


def upsert_vectors(chunks: list[dict], embeddings: list[list[float]], batch_size: int = 50):
    """
    Batch upsert embedded chunks into Endee with metadata for source attribution.

    Each vector includes:
    - meta.text: the chunk text (for display in results)
    - meta.source: originating document filename
    - meta.page: page number in the PDF
    - filter.doc_type: "medical" (for filtered queries)
    """
    client = get_client()
    index = client.get_index(name=INDEX_NAME)

    total = len(chunks)
    for i in range(0, total, batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]

        vectors = []
        for chunk, embedding in zip(batch_chunks, batch_embeddings):
            vectors.append({
                "id": chunk["id"],
                "vector": embedding,
                "meta": {
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "page": chunk["page"],
                },
                "filter": {
                    "doc_type": "medical",
                },
            })

        index.upsert(vectors)
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        logger.info(f"Upserted batch {batch_num}/{total_batches} ({len(vectors)} vectors)")

    logger.info(f"Successfully upserted {total} vectors into '{INDEX_NAME}'")
