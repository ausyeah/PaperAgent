from typing import Union
import os

from paperagent.models import ParsedPaper
from paperagent.parser.arxiv import is_arxiv_source, download_arxiv_pdf
from paperagent.parser.mineru_adapter import parse_with_mineru
from paperagent.parser.pdf_extractor import extract_from_pdf

def parse_paper(source: str) -> ParsedPaper:
    """
    Parse an academic paper from an ArXiv ID, URL, or local PDF path.
    Returns a structured ParsedPaper object.
    """
    if is_arxiv_source(source):
        # Delegate to ArXiv downloader first
        pdf_bytes = download_arxiv_pdf(source)
        # Pass bytes to adapter (which tries Mineru, falls back to pdf_extractor)
        parsed = parse_with_mineru(pdf_bytes, is_arxiv=True)
        parsed.source_type = "arxiv"
        if not parsed.metadata.arxiv_id:
            from paperagent.parser.arxiv import extract_arxiv_id
            parsed.metadata.arxiv_id = extract_arxiv_id(source)
        return parsed
    elif os.path.exists(source):
        parsed = parse_with_mineru(source, is_arxiv=False)
        parsed.source_type = "local_pdf"
        return parsed
    else:
        raise ValueError(f"Source {source} is not a valid ArXiv ID/URL or local file path.")

__all__ = ["parse_paper", "extract_from_pdf", "parse_with_mineru"]
