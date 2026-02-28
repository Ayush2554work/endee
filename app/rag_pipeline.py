"""
HemaV MedAssist — RAG Pipeline Orchestration

Ties together the full Retrieval-Augmented Generation pipeline:
Query → Embed → Retrieve from Endee → Build Context → LLM Answer

This is textbook RAG — the industry standard approach for grounding
LLM responses in actual documents while minimizing hallucination.
"""
import logging
from endee_integration.retriever import retrieve, build_context
from app.llm import generate_answer

logger = logging.getLogger("hemav.app.rag")


class RAGPipeline:
    """End-to-end RAG pipeline for medical Q&A."""

    def query(self, question: str, api_key: str = None) -> dict:
        """
        Process a user question through the full RAG pipeline.

        Pipeline:
        1. Embed query using Sentence Transformers
        2. Search Endee for top-k similar medical document chunks
        3. Build context string with source attribution
        4. Send context + question to Groq LLM
        5. Return answer with sources and confidence scores

        Returns:
            dict with: question, answer, sources, context_used
        """
        logger.info(f"RAG query: '{question[:80]}...'")

        # Step 1 & 2: Retrieve relevant chunks from Endee
        results = retrieve(question)
        logger.info(f"Retrieved {len(results)} chunks from Endee")

        # Step 3: Build context string
        context = build_context(results)

        # Step 4: Generate answer using LLM
        answer = generate_answer(question, context, api_key)

        # Step 5: Return structured response
        return {
            "question": question,
            "answer": answer,
            "sources": results,
            "context_used": context,
        }
