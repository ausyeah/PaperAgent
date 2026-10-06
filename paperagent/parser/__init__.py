"""
PaperAgent Parser Subpackage
Unified entry points for paper ingestion, ArXiv querying, and PDF parsing.
"""

from typing import Union
import os
from pathlib import Path

from paperagent.models import ParsedPaper, PaperMetadata
from paperagent.parser.arxiv import (
    is_arxiv_source,
    extract_arxiv_id,
    fetch_arxiv_metadata,
    download_arxiv_pdf,
)
from paperagent.parser.mineru_adapter import parse_with_mineru
from paperagent.parser.pdf_extractor import extract_from_pdf
from paperagent.parser.table_extractor import TableExtractor


def parse_paper(source: str) -> ParsedPaper:
    """
    Parse an academic paper from an ArXiv ID, URL, or local PDF path.
    Returns a structured ParsedPaper object.
    """
    if is_arxiv_source(source):
        arxiv_id = extract_arxiv_id(source)
        if not arxiv_id:
            raise ValueError(f"Could not extract valid ArXiv ID from: {source}")
        
        # Try fetching official metadata from ArXiv API
        meta = None
        try:
            meta = fetch_arxiv_metadata(arxiv_id)
        except Exception:
            pass

        # Download PDF to cache
        pdf_path = download_arxiv_pdf(arxiv_id)

        # Parse downloaded PDF
        parsed = parse_with_mineru(pdf_path, is_arxiv=True)
        parsed.source_type = "arxiv"

        if meta:
            parsed.metadata = meta
        else:
            parsed.metadata.arxiv_id = arxiv_id

        return parsed

    elif os.path.exists(source):
        parsed = parse_with_mineru(source, is_arxiv=False)
        parsed.source_type = "local_pdf"
        return parsed

    else:
        raise ValueError(f"Source '{source}' is not a valid ArXiv ID/URL or existing file path.")


__all__ = [
    "parse_paper",
    "extract_from_pdf",
    "parse_with_mineru",
    "is_arxiv_source",
    "extract_arxiv_id",
    "fetch_arxiv_metadata",
    "download_arxiv_pdf",
    "TableExtractor",
]
