"""
HemaV MedAssist — Endee Vector DB: Retriever

Handles semantic search against Endee for the RAG pipeline.
Converts user queries to embeddings, searches for top-k similar
chunks, and builds context with confidence scores and source attribution.
"""
import json
import logging
import os
from datetime import datetime
from config import INDEX_NAME, TOP_K, LOGS_DIR
from embeddings.generator import generate_single_embedding
from endee_integration.indexer import get_client

logger = logging.getLogger("hemav.endee.retriever")


def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Semantic search pipeline:
    1. Convert query → embedding
    2. Query Endee for top-k similar chunks (cosine similarity)
    3. Return results with confidence scores and source metadata

    Returns:
        List of dicts with: id, text, source, page, similarity (confidence score)
    """
    # Step 1: Generate query embedding
    query_embedding = generate_single_embedding(query)

    # Step 2: Query Endee
    client = get_client()
    index = client.get_index(name=INDEX_NAME)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        ef=128,  # HNSW exploration factor — higher = more accurate but slower
    )

    # Step 3: Format results with confidence scores
    retrieved = []
    for item in results:
        meta = item.get("meta", {})
        retrieved.append({
            "id": item.get("id", ""),
            "text": meta.get("text", ""),
            "source": meta.get("source", ""),
            "page": meta.get("page", ""),
            "similarity": round(item.get("similarity", 0.0), 4),  # confidence score
        })

    # Log retrieval results for debugging and evaluation
    _log_retrieval(query, retrieved)

    return retrieved


def build_context(results: list[dict]) -> str:
    """
    Build formatted context string from retrieved results.
    Includes source attribution for each chunk.
    """
    if not results:
        return "No relevant documents found in the knowledge base."

    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(
            f"[Source {i}: {r['source']}, Page {r['page']}] "
            f"(Confidence: {r['similarity']:.2%})\n{r['text']}"
        )

    return "\n\n---\n\n".join(context_parts)


def _log_retrieval(query: str, results: list[dict]):
    """
    Log retrieval results to a JSON file for evaluation and debugging.
    Shows which chunks were retrieved, their confidence scores, and sources.
    """
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
        log_file = os.path.join(LOGS_DIR, "retrieval_log.jsonl")

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "num_results": len(results),
            "results": [
                {
                    "id": r["id"],
                    "source": r["source"],
                    "page": r["page"],
                    "similarity": r["similarity"],
                    "text_preview": r["text"][:100] + "..." if len(r["text"]) > 100 else r["text"],
                }
                for r in results
            ],
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        logger.debug(f"Logged retrieval for query: '{query[:50]}...'")
    except Exception as e:
        logger.warning(f"Failed to log retrieval: {e}")
