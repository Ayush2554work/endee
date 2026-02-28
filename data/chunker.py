"""
HemaV MedAssist — Text Chunking

Why chunk size matters:
- Too large → embeddings lose specificity, retrieval returns broad passages
- Too small → context is fragmented, LLM lacks sufficient information
- 500 chars with 50-char overlap is optimal for medical text:
  * Preserves complete medical statements
  * Overlap ensures no information is lost at boundaries
  * Keeps chunks focused enough for precise retrieval
"""
import logging
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger("hemav.data.chunker")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks with sentence-boundary awareness.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size

        # Break at sentence boundary for cleaner chunks
        if end < len(text):
            last_period = text.rfind('. ', start, end)
            last_newline = text.rfind('\n', start, end)
            break_point = max(last_period, last_newline)
            if break_point > start + chunk_size // 2:
                end = break_point + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Chunk a list of page dicts, preserving metadata for source attribution.
    """
    all_chunks = []
    chunk_id = 0

    for page in pages:
        text_chunks = chunk_text(page["text"])
        for i, chunk in enumerate(text_chunks):
            all_chunks.append({
                "id": f"{page['source']}_p{page['page']}_c{i}",
                "text": chunk,
                "page": page["page"],
                "source": page["source"],
                "chunk_index": chunk_id,
            })
            chunk_id += 1

    logger.info(f"Created {len(all_chunks)} chunks from {len(pages)} pages")
    return all_chunks
