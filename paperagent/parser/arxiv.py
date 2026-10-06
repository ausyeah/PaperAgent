import re
import urllib.request
from typing import Optional

def is_arxiv_source(source: str) -> bool:
    """Check if the source is an ArXiv ID or URL."""
    # Match arxiv ID format: \d{4}\.\d{4,5} or arxiv urls
    if re.search(r'\d{4}\.\d{4,5}', source):
        return True
    if 'arxiv.org' in source.lower():
        return True
    return False

def extract_arxiv_id(source: str) -> Optional[str]:
    """Extract the ArXiv ID from a source string."""
    match = re.search(r'(\d{4}\.\d{4,5}(v\d+)?)', source)
    if match:
        return match.group(1)
    return None

def download_arxiv_pdf(source: str) -> bytes:
    """
    Download the PDF bytes from ArXiv given an ID or URL.
    """
    arxiv_id = extract_arxiv_id(source)
    if not arxiv_id:
        raise ValueError(f"Could not extract ArXiv ID from {source}")

    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read()
