"""
HemaV MedAssist — FastAPI Web Application

Serves the premium web UI and provides API endpoints for:
- RAG queries (semantic search + LLM answer generation)
- Health checks (Endee connection status)
"""
import logging
import markdown
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from app.rag_pipeline import RAGPipeline

logger = logging.getLogger("hemav.app.server")

app = FastAPI(
    title="HemaV MedAssist",
    description="AI-Powered Medical RAG Assistant using Endee Vector Database",
    version="1.0.0",
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize RAG pipeline
pipeline = RAGPipeline()


class QueryRequest(BaseModel):
    question: str
    api_key: str = None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/query")
async def query(req: QueryRequest):
    """API endpoint for RAG queries."""
    question = req.question.strip()

    if not question:
        return JSONResponse({"error": "Please enter a question."}, status_code=400)

    try:
        result = pipeline.query(question, api_key=req.api_key)

        # Convert markdown in answer to HTML for rendering
        answer_html = markdown.markdown(
            result["answer"],
            extensions=["fenced_code", "tables", "nl2br"],
        )

        return {
            "answer": answer_html,
            "answer_raw": result["answer"],
            "sources": result["sources"],
            "question": result["question"],
        }
    except Exception as e:
        logger.error(f"Query error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/health")
async def health():
    """Health check — verifies Endee connection."""
    try:
        from endee_integration.indexer import get_client
        client = get_client()
        indexes = client.list_indexes()
        return {
            "status": "healthy",
            "endee_connected": True,
            "indexes": len(indexes),
        }
    except Exception as e:
        return {
            "status": "degraded",
            "endee_connected": False,
            "error": str(e),
        }
