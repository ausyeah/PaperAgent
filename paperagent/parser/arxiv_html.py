import httpx
from typing import Optional

def fetch_arxiv_html(arxiv_id: str, timeout: float = 15.0) -> Optional[str]:
    """
    Fetches the experimental HTML version of an ArXiv paper.

    Args:
        arxiv_id: The ArXiv ID (e.g., '2312.12456').
        timeout: Request timeout in seconds.

    Returns:
        The HTML content as a string if successful (200 OK), or None if
        it returns 404 or a request error occurs.
    """
    url = f"https://arxiv.org/html/{arxiv_id}"
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        if response.status_code == 200:
            return response.text
        return None
    except httpx.RequestError:
        return None


from bs4 import BeautifulSoup
from paperagent.models import (
    ParsedPaper, PaperMetadata, PaperSection, ExtractedFormula, ExtractedAlgorithm
)
import uuid

def parse_arxiv_html(html_content: str, arxiv_id: str) -> ParsedPaper:
    """
    Parses ArXiv HTML content into a structured ParsedPaper object.

    Args:
        html_content: The HTML content.
        arxiv_id: The ArXiv ID.

    Returns:
        A ParsedPaper object.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract Title
    title = "Unknown Title"
    title_elem = soup.find('h1', class_='ltx_title') or soup.find('h1', class_='title') or soup.find('title')
    if title_elem:
        title = title_elem.get_text(strip=True)

    # Extract Authors
    authors = []
    author_elems = soup.find_all(class_='ltx_author') + soup.find_all(class_='authors') + soup.find_all('span', class_='author')
    for a in author_elems:
        name = a.get_text(strip=True)
        if name and name not in authors:
            authors.append(name)

    # Extract Abstract
    abstract = ""
    abstract_elem = soup.find('div', class_='ltx_abstract')
    if abstract_elem:
        abstract = abstract_elem.get_text(strip=True)
    else:
        # Fallback abstract check
        for sec in soup.find_all('section'):
            h2 = sec.find('h2')
            if h2 and 'abstract' in h2.get_text(strip=True).lower():
                abstract = sec.get_text(strip=True)
                break

    metadata = PaperMetadata(
        title=title,
        authors=authors,
        abstract=abstract,
        arxiv_id=arxiv_id,
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    )

    # Sections
    sections = []
    section_elems = soup.find_all('section', class_='ltx_section')
    if not section_elems:
        section_elems = soup.find_all('section')

    for sec in section_elems:
        sec_title_elem = sec.find('h2', class_='ltx_title') or sec.find('h2')
        sec_title = sec_title_elem.get_text(strip=True) if sec_title_elem else "Untitled Section"

        # Don't include abstract as a general section if we already have it
        if 'abstract' in sec_title.lower():
            continue

        paragraphs = []
        for p in sec.find_all('p'):
            paragraphs.append(p.get_text(strip=True))

        sections.append(PaperSection(
            title=sec_title,
            level=1,
            content="\n\n".join(paragraphs)
        ))

    # We will put all formulas and algorithms into the first section if one exists,
    # or create a dummy section if there are none, because ParsedPaper only stores them inside PaperSection.

    # Formulas
    formulas = []
    math_elems = soup.find_all(['math', 'span', 'div'], class_=['ltx_Math', 'ltx_equation', None])
    # Also find standalone <math> tags
    all_math = soup.find_all('math') + soup.find_all(class_='ltx_Math') + soup.find_all(class_='ltx_equation')

    # remove duplicates by id or content
    seen_math = set()
    for m in all_math:
        # Try alttext attribute
        latex = m.get('alttext')
        if not latex:
            # Fallback to text content if it looks like math
            latex = m.get_text(strip=True)

        if not latex or len(latex) < 2 or latex in seen_math:
            continue

        seen_math.add(latex)

        # Extract context
        context = ""
        parent_p = m.find_parent('p')
        if parent_p:
            context = parent_p.get_text(strip=True)[:200]

        formulas.append(ExtractedFormula(
            id=f"eq-{uuid.uuid4().hex[:8]}",
            latex=latex,
            context_text=context
        ))

    # Algorithms
    algorithms = []
    algo_elems = soup.find_all(['figure', 'div'], class_='ltx_algorithm')
    # fallback searching for "Algorithm" blocks
    if not algo_elems:
        for div in soup.find_all('div'):
            text = div.get_text(strip=True)
            if text.startswith('Algorithm '):
                algo_elems.append(div)

    for a in algo_elems:
        caption = a.find('figcaption') or a.find('div', class_='ltx_caption')
        name = caption.get_text(strip=True) if caption else "Untitled Algorithm"

        # Extract pseudocode
        pseudocode_lines = []
        for line in a.find_all(['div', 'span', 'p']):
            line_text = line.get_text(strip=True)
            # basic filtering to avoid caption
            if line_text and line_text != name:
                pseudocode_lines.append(line_text)

        pseudocode = "\n".join(pseudocode_lines)
        if not pseudocode:
            pseudocode = a.get_text(strip=True)

        algorithms.append(ExtractedAlgorithm(
            id=f"algo-{uuid.uuid4().hex[:8]}",
            name=name,
            pseudocode=pseudocode
        ))

    # Add formulas and algorithms to sections
    if formulas or algorithms:
        if not sections:
            sections.append(PaperSection(title="Extracted Content", level=1, content=""))

        # Attach to the last section for simplicity if we just have a flat list,
        # or root section. Here we attach them to the first section.
        sections[0].formulas.extend(formulas)
        sections[0].algorithms.extend(algorithms)

    raw_text = soup.get_text(separator="\n", strip=True)

    return ParsedPaper(
        metadata=metadata,
        sections=sections,
        raw_markdown=raw_text,
        source_type="arxiv_html"
    )

from paperagent.parser.arxiv import extract_arxiv_id, fetch_arxiv_metadata
from paperagent.parser import parse_paper

def extract_paper_from_arxiv_source(source: str) -> ParsedPaper:
    """
    Extracts a ParsedPaper from an ArXiv source, preferring HTML parsing
    with a fallback to PDF parsing.

    Args:
        source: The ArXiv ID or URL.

    Returns:
        A ParsedPaper object.

    Raises:
        ValueError: If a valid ArXiv ID cannot be extracted from the source.
    """
    arxiv_id = extract_arxiv_id(source)
    if not arxiv_id:
        raise ValueError(f"Could not extract valid ArXiv ID from: {source}")

    # Attempt HTML fetch
    html_content = fetch_arxiv_html(arxiv_id)
    if html_content:
        # We got HTML!
        return parse_arxiv_html(html_content, arxiv_id)

    # Fallback to PDF parsing if HTML isn't available
    # parse_paper already handles fetch_arxiv_metadata and PDF download internally
    return parse_paper(source)
