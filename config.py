"""
HemaV MedAssist — Central Configuration
All environment variables, constants, and prompt templates.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq LLM ────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = "llama-3.3-70b-versatile"

# ── Endee Vector DB ─────────────────────────────────────────
ENDEE_HOST = os.getenv("ENDEE_HOST", "http://localhost:8080")
ENDEE_AUTH_TOKEN = os.getenv("ENDEE_AUTH_TOKEN", "")
INDEX_NAME = "hemav_medical_docs"

# ── Embedding ───────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))

# ── RAG settings ────────────────────────────────────────────
TOP_K = int(os.getenv("TOP_K", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# ── Paths ───────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
MEDICAL_DOCS_DIR = os.path.join(BASE_DIR, "data", "medical_docs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# ── System Prompt ───────────────────────────────────────────
SYSTEM_PROMPT = """You are HemaV MedAssist, an AI-powered medical knowledge assistant specializing in hematology and anemia-related topics.
Your underlying architecture uses the Endee Vector Database for semantic search and retrieval, and you are powered by the Groq Llama 3 LLM.

RULES:
1. For medical queries, answer ONLY based on the provided context from medical documents.
2. If the context doesn't contain enough information for a medical query, clearly state: "I don't have enough information in my knowledge base to answer this accurately."
3. Always cite which source document and page the information comes from using [Source X] notation.
4. Include a brief medical disclaimer at the end of each response.
5. Never provide direct medical diagnoses — always recommend consulting a healthcare professional.
6. Be precise, clear, and use medical terminology appropriately while keeping explanations accessible.
7. Format your responses with clear headings, bullet points, and structured information when appropriate.
8. If the user asks about you, your architecture, or whether you use Groq/Endee, you are allowed to answer truthfully without needing document context.

DISCLAIMER TO INCLUDE:
⚕️ *This information is for educational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.*
"""

USER_PROMPT_TEMPLATE = """Based on the following medical knowledge context, answer the user's question.

CONTEXT FROM MEDICAL DOCUMENTS:
{context}

USER QUESTION: {question}

Provide a comprehensive, well-structured answer with citations to the source documents [Source 1], [Source 2], etc. Remember to include the medical disclaimer.
"""
