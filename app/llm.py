"""
HemaV MedAssist — LLM Integration (Groq)

Uses Groq API with Llama 3.3 70B Versatile for grounded answer generation.

Why RAG reduces hallucination:
- Without RAG: LLM generates answers purely from training data → can hallucinate facts
- With RAG: LLM is given actual document chunks as context → answers are grounded in evidence
- The system prompt restricts answers to ONLY the provided context
- Source citations let users verify claims against original documents
- If context is insufficient, the model explicitly says so instead of guessing
"""
import logging
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger("hemav.app.llm")


def get_groq_client(custom_api_key: str = None) -> Groq:
    """Initialize the Groq client with a custom key if provided."""
    key = custom_api_key if custom_api_key else GROQ_API_KEY
    if not key:
        raise ValueError("No Groq API key found. Please provide one in the UI or .env")
    return Groq(api_key=key)


def generate_answer(question: str, context: str, api_key: str = None) -> str:
    """
    Send question + retrieved context to Groq LLM.
    Returns a grounded answer with source citations and medical disclaimer.
    """
    client = get_groq_client(api_key)

    user_message = USER_PROMPT_TEMPLATE.format(
        context=context,
        question=question,
    )

    try:
        chat_completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,   # Low temp for factual accuracy
            max_tokens=2048,
            top_p=0.9,
        )

        answer = chat_completion.choices[0].message.content
        logger.info(f"Generated answer ({len(answer)} chars) for query: '{question[:50]}...'")
        return answer

    except Exception as e:
        logger.error(f"LLM error: {e}")
        return f"❌ Error generating answer: {str(e)}\n\nPlease check your GROQ_API_KEY in the .env file."
