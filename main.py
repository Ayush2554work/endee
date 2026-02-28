#!/usr/bin/env python3
"""
HemaV MedAssist — Main Entry Point

Starts the FastAPI web application.
Usage:
    python main.py              # Start the web server
    python main.py --ingest     # Ingest documents then start server
    python main.py --ingest-only # Only ingest, don't start server
"""
import argparse
import logging
import os
import sys
import uvicorn

# ── Logging Setup ───────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-28s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("hemav.main")


def run_ingestion(pdf_path: str = None, directory: str = None):
    """Run the data ingestion pipeline."""
    from data.pdf_parser import extract_text_from_pdf, extract_from_directory
    from data.chunker import chunk_pages
    from embeddings.generator import generate_embeddings
    from endee_integration.indexer import create_index, upsert_vectors
    from config import DATA_DIR

    print(f"\n{'='*60}")
    print(f"  HemaV MedAssist — Data Ingestion Pipeline")
    print(f"{'='*60}\n")

    # Determine what to ingest
    if pdf_path:
        if not os.path.exists(pdf_path):
            print(f"  ❌ File not found: {pdf_path}")
            sys.exit(1)
        print(f"📖 Step 1: Extracting text from {pdf_path}...")
        pages = extract_text_from_pdf(pdf_path)
    elif directory:
        if not os.path.isdir(directory):
            print(f"  ❌ Directory not found: {directory}")
            sys.exit(1)
        print(f"📖 Step 1: Extracting text from all PDFs in {directory}...")
        pages = extract_from_directory(directory)
    else:
        # Default: ingest data/raw/ + data/medical_docs/
        pages = []

        if os.path.isdir(DATA_DIR):
            print(f"📖 Step 1a: Extracting text from data/raw/...")
            pages.extend(extract_from_directory(DATA_DIR))

        from config import MEDICAL_DOCS_DIR
        if os.path.isdir(MEDICAL_DOCS_DIR):
            print(f"📖 Step 1b: Extracting text from data/medical_docs/...")
            pages.extend(extract_from_directory(MEDICAL_DOCS_DIR))

    if not pages:
        print("  ❌ No text extracted from any source.")
        sys.exit(1)

    print(f"  ✅ Extracted {len(pages)} pages total\n")

    # Step 2: Chunk
    print("🔪 Step 2: Chunking text (500 chars, 50 overlap)...")
    chunks = chunk_pages(pages)

    # Step 3: Embed
    print("\n🧠 Step 3: Generating embeddings (all-MiniLM-L6-v2, 384-dim)...")
    texts = [c["text"] for c in chunks]
    embeddings = generate_embeddings(texts)
    print(f"  ✅ Generated {len(embeddings)} embeddings\n")

    # Step 4: Index into Endee
    print("🗄️  Step 4: Indexing into Endee Vector Database...")
    create_index()
    upsert_vectors(chunks, embeddings)

    print(f"\n{'='*60}")
    print(f"  ✅ Ingestion complete! {len(chunks)} vectors indexed in Endee")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="HemaV MedAssist — AI Medical RAG Assistant")
    parser.add_argument("--ingest", action="store_true", help="Ingest documents before starting server")
    parser.add_argument("--ingest-only", action="store_true", help="Only ingest documents, don't start server")
    parser.add_argument("--file", type=str, help="Path to a specific PDF to ingest")
    parser.add_argument("--dir", type=str, help="Directory of PDFs to ingest")
    parser.add_argument("--port", type=int, default=5000, help="Server port (default: 5000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    args = parser.parse_args()

    # Run ingestion if requested
    if args.ingest or args.ingest_only:
        run_ingestion(pdf_path=args.file, directory=args.dir)
        if args.ingest_only:
            return
    else:
        # Auto-ingest if Endee is running but index doesn't exist
        try:
            from endee_integration.indexer import get_client
            from config import INDEX_NAME
            client = get_client()
            client.get_index(name=INDEX_NAME)
        except Exception as e:
            if "ConnectionError" in str(type(e)):
                print(f"⚠️ Warning: Could not connect to Endee Vector Database.")
                print(f"   Ensure Docker is running `endeespace/endee:latest` on port 8080.")
            else:
                print(f"⚠️ Index '{INDEX_NAME}' not found. Running automatic ingestion...")
                run_ingestion()

    # Start the web server
    print(f"\n🚀 Starting HemaV MedAssist on http://{args.host}:{args.port}")
    print(f"   Press Ctrl+C to stop\n")
    uvicorn.run("app.server:app", host=args.host, port=args.port, reload=True)


if __name__ == "__main__":
    main()
