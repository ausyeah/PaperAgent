import re
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from typing import Optional
from pathlib import Path

from paperagent.models import PaperMetadata
from paperagent.config import settings

def extract_arxiv_id(input_str: str) -> Optional[str]:
    """
    Extracts an ArXiv ID from a pure ID string or an ArXiv URL.

    Args:
        input_str: The string containing the ArXiv ID or URL.

    Returns:
        The extracted ArXiv ID if found, otherwise None.
    """
    # Regex to capture modern ArXiv IDs (e.g. 2312.12456, 2312.12456v2)
    # and old-style IDs (e.g. math/0501001, math.AG/0501001v2)
    pattern = r'(?:arxiv\.org/(?:abs|pdf|html)/)?([a-z\-]+(?:\.[a-zA-Z]{2})?/\d{7}(?:v\d+)?|\d{4}\.\d{4,5}(?:v\d+)?)'

    match = re.search(pattern, input_str)
    if match:
        return match.group(1)

    return None

def fetch_arxiv_metadata(arxiv_id: str) -> PaperMetadata:
    """
    Fetches paper metadata from the ArXiv API.

    Args:
        arxiv_id: The ArXiv ID to query.

    Returns:
        A PaperMetadata object containing the parsed metadata.

    Raises:
        ValueError: If the API request fails or the response cannot be parsed.
    """
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            xml_data = response.read()
    except urllib.error.URLError as e:
        raise ValueError(f"Failed to fetch metadata from ArXiv API: {e}")

    try:
        root = ET.fromstring(xml_data)

        # ArXiv API uses Atom XML namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}

        entry = root.find('atom:entry', ns)
        if entry is None:
            raise ValueError(f"No results found for ArXiv ID: {arxiv_id}")

        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        abstract = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')

        authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]

        published = entry.find('atom:published', ns).text
        year = int(published[:4]) if published else None

        categories = [category.attrib['term'] for category in entry.findall('atom:category', ns)]

        doi = None
        doi_elem = entry.find('arxiv:doi', ns)
        if doi_elem is not None:
            doi = doi_elem.text

        pdf_url = None
        for link in entry.findall('atom:link', ns):
            if link.attrib.get('title') == 'pdf':
                pdf_url = link.attrib.get('href')
                break

        # Fallback if no explicit pdf link is provided but we can construct it
        if not pdf_url:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        return PaperMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
            arxiv_id=arxiv_id,
            doi=doi,
            year=year,
            categories=categories,
            pdf_url=pdf_url
        )
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse ArXiv API response: {e}")
    except AttributeError as e:
        raise ValueError(f"Missing required fields in ArXiv API response: {e}")

def download_arxiv_pdf(arxiv_id: str, output_path: Optional[str] = None) -> str:
    """
    Downloads the PDF for a given ArXiv ID.

    Args:
        arxiv_id: The ArXiv ID of the paper.
        output_path: Optional path to save the PDF. If not provided, it saves to cache_dir.

    Returns:
        The file path where the PDF was saved.

    Raises:
        ValueError: If the download fails.
    """
    if output_path is None:
        settings.init_directories()
        # Clean arxiv_id to avoid slash issues in filename (e.g. for old-style IDs)
        safe_id = arxiv_id.replace('/', '_')
        output_file = settings.cache_dir / f"{safe_id}.pdf"
    else:
        output_file = Path(output_path)

    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    try:
        urllib.request.urlretrieve(pdf_url, output_file)
        return str(output_file)
    except urllib.error.URLError as e:
        raise ValueError(f"Failed to download PDF from {pdf_url}: {e}")
