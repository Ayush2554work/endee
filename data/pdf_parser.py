"""
HemaV MedAssist — PDF Text Extraction
Extracts text from PDF files page-by-page with source metadata.
"""
import os
import logging
from PyPDF2 import PdfReader

logger = logging.getLogger("hemav.data.pdf_parser")


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from a PDF file, returning structured page data.

    Returns:
        List of dicts with keys: text, page, source
    """
    reader = PdfReader(pdf_path)
    filename = os.path.basename(pdf_path)
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({
                "text": text.strip(),
                "page": i + 1,
                "source": filename,
            })

    logger.info(f"Extracted {len(pages)} pages from {filename}")
    return pages


def extract_text_from_txt(txt_path: str) -> list[dict]:
    """
    Extract text from a .txt file.
    Splits into ~1000 char segments to simulate page-like structure.
    """
    filename = os.path.basename(txt_path)
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into page-like segments (~1000 chars each, break at paragraph)
    segments = []
    paragraphs = content.split("\n\n")
    current = ""
    page_num = 1

    for para in paragraphs:
        if len(current) + len(para) > 1000 and current:
            segments.append({"text": current.strip(), "page": page_num, "source": filename})
            page_num += 1
            current = para
        else:
            current += "\n\n" + para if current else para

    if current.strip():
        segments.append({"text": current.strip(), "page": page_num, "source": filename})

    logger.info(f"Extracted {len(segments)} segments from {filename}")
    return segments


def extract_from_directory(dir_path: str) -> list[dict]:
    """Extract text from all PDFs and TXT files in a directory."""
    all_pages = []
    if not os.path.isdir(dir_path):
        logger.warning(f"Directory not found: {dir_path}")
        return all_pages

    for fname in sorted(os.listdir(dir_path)):
        fpath = os.path.join(dir_path, fname)
        if fname.lower().endswith(".pdf"):
            all_pages.extend(extract_text_from_pdf(fpath))
        elif fname.lower().endswith(".txt"):
            all_pages.extend(extract_text_from_txt(fpath))

    logger.info(f"Total pages extracted from directory: {len(all_pages)}")
    return all_pages
