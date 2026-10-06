from typing import Union
import logging
from paperagent.models import ParsedPaper
from paperagent.config import settings
from paperagent.parser.pdf_extractor import extract_from_pdf

logger = logging.getLogger(__name__)

def parse_with_mineru(source: Union[str, bytes], is_arxiv: bool = False) -> ParsedPaper:
    """
    Attempt to use Mineru cloud API for high-fidelity extraction.
    If the API key is not configured or the call fails, cleanly fallback
    to the local PDF extractor.
    """
    mineru_key = settings.mineru_api_key

    if mineru_key:
        try:
            # Placeholder for actual Mineru API call.
            # In a real implementation, we would send the PDF or ArXiv ID to Mineru,
            # parse the resulting structured data, and return a ParsedPaper.
            # For now, we simulate an API that hasn't been implemented yet and trigger the fallback.
            raise NotImplementedError("Mineru API client not fully implemented.")
        except Exception as e:
            logger.warning(f"Mineru extraction failed ({str(e)}), falling back to local extractor.")
            # Fallback to local
            pass
    else:
        logger.info("Mineru API key not found, using local PDF extractor.")

    return extract_from_pdf(source)
