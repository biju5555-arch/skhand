"""Load and parse scientific PDFs for ingestion."""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from skhand.config import get_settings
from skhand.ingestion.chunker import Chunk, chunk_text_by_size
from skhand.utils.display import console


def load_papers(data_dir: Path | None = None) -> list[Chunk]:
    """Load all PDFs from the papers directory."""
    settings = get_settings()
    data_dir = data_dir or settings.papers_data_dir

    if not data_dir.exists():
        console.print(f"[warning]Papers directory not found: {data_dir}[/warning]")
        return []

    all_chunks = []
    pdf_files = list(data_dir.glob("**/*.pdf"))

    if not pdf_files:
        console.print("[warning]No PDF files found[/warning]")
        return []

    for pdf_path in pdf_files:
        console.print(f"[meta]Processing {pdf_path.name}...[/meta]")
        chunks = _parse_pdf(pdf_path)
        all_chunks.extend(chunks)

    console.print(f"[success]Loaded {len(all_chunks)} chunks from {len(pdf_files)} papers[/success]")
    return all_chunks


def _parse_pdf(pdf_path: Path) -> list[Chunk]:
    """Parse a single PDF and return chunks."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        console.print(f"[error]Failed to open {pdf_path.name}: {e}[/error]")
        return []

    metadata = _extract_metadata(doc, pdf_path)
    full_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            full_text.append(text)

    doc.close()

    if not full_text:
        return []

    combined = "\n\n".join(full_text)
    chunks = chunk_text_by_size(
        combined,
        chunk_size=1000,
        overlap=200,
        metadata={
            **metadata,
            "type": "scientific_paper",
        },
    )

    return chunks


def _extract_metadata(doc: fitz.Document, pdf_path: Path) -> dict:
    """Extract metadata from PDF document."""
    pdf_meta = doc.metadata or {}

    # Determine category from directory structure
    category = pdf_path.parent.name  # e.g., "bhasma" or "nanoparticle"

    return {
        "source": pdf_path.stem,
        "title": pdf_meta.get("title", pdf_path.stem),
        "author": pdf_meta.get("author", ""),
        "category": category,
        "filename": pdf_path.name,
    }
