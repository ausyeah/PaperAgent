import re
import io
import uuid
from typing import List, Union
from pypdf import PdfReader
from paperagent.models import (
    ParsedPaper,
    PaperMetadata,
    PaperSection,
    ExtractedFormula,
    ExtractedAlgorithm
)

def clean_text(text: str) -> str:
    """Clean header/footer artifacts and extra spaces."""
    # Remove lines that are just numbers (likely page numbers)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        sline = line.strip()
        if re.match(r'^\d+$', sline):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def extract_formulas(text: str) -> List[ExtractedFormula]:
    """Extract mathematical formulas using regex heuristics."""
    formulas = []

    # 1. Display equations: $$ ... $$
    display_matches = re.finditer(r'\$\$(.*?)\$\$', text, re.DOTALL)
    for m in display_matches:
        latex = m.group(1).strip()
        f = ExtractedFormula(
            id=f"eq-{uuid.uuid4().hex[:8]}",
            latex=latex,
            context_text=""
        )
        formulas.append(f)

    # 2. Block equations: \[ ... \]
    block_matches = re.finditer(r'\\\[(.*?)\\\]', text, re.DOTALL)
    for m in block_matches:
        latex = m.group(1).strip()
        f = ExtractedFormula(
            id=f"eq-{uuid.uuid4().hex[:8]}",
            latex=latex,
            context_text=""
        )
        formulas.append(f)

    # 3. Environment equations: \begin{equation} ... \end{equation}
    env_matches = re.finditer(r'\\begin\{equation\}(.*?)\\end\{equation\}', text, re.DOTALL)
    for m in env_matches:
        latex = m.group(1).strip()
        f = ExtractedFormula(
            id=f"eq-{uuid.uuid4().hex[:8]}",
            latex=latex,
            context_text=""
        )
        formulas.append(f)

    # 4. Inline equations: $ ... $ (be careful not to match $$)
    # We replace $$ with a placeholder first to avoid inline matching them
    temp_text = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
    inline_matches = re.finditer(r'\$([^$\n]+)\$', temp_text)
    for m in inline_matches:
        latex = m.group(1).strip()
        f = ExtractedFormula(
            id=f"eq-{uuid.uuid4().hex[:8]}",
            latex=latex,
            context_text=""
        )
        formulas.append(f)

    return formulas

def extract_algorithms(text: str) -> List[ExtractedAlgorithm]:
    """Extract algorithm blocks from text."""
    algorithms = []
    # Try to find something that looks like an algorithm block
    # Looks for "Algorithm X", optionally a caption, then "Input:" or "Output:" and pseudocode
    algo_pattern = re.compile(
        r'(Algorithm\s+\d+[:\.]?\s*(.*?))\n(?:.*?)'
        r'(?:(Input|Require):\s*(.*?)\n)?'
        r'(?:(Output|Ensure):\s*(.*?)\n)?'
        r'(.*?)(?=(Algorithm\s+\d+|$))',
        re.DOTALL | re.IGNORECASE
    )

    # We will use a simpler approach because regex over huge text for algorithms is brittle.
    # Let's split by lines and look for "Algorithm" and "Input"/"Output"

    lines = text.split('\n')
    in_algo = False
    current_algo = None

    for i, line in enumerate(lines):
        sline = line.strip()
        if re.match(r'^Algorithm\s+\d+', sline, re.IGNORECASE):
            if current_algo:
                algorithms.append(current_algo)

            # Start new algorithm
            name_match = re.match(r'^(Algorithm\s+\d+[:\.]?\s*(.*))$', sline, re.IGNORECASE)
            algo_name = name_match.group(1).strip() if name_match else sline

            current_algo = ExtractedAlgorithm(
                id=f"algo-{uuid.uuid4().hex[:8]}",
                name=algo_name,
                pseudocode="",
                inputs=[],
                outputs=[]
            )
            in_algo = True
            continue

        if in_algo:
            # Check for next section or normal text continuing
            # This is a heuristic: if we see a numeric header like "3. Methodology" we probably left the algo
            if re.match(r'^\d+\.\s+[A-Z]', sline):
                algorithms.append(current_algo)
                current_algo = None
                in_algo = False
                continue

            input_match = re.match(r'^(?:Input|Require)s?:\s*(.*)', sline, re.IGNORECASE)
            if input_match:
                inp = input_match.group(1).strip()
                if inp:
                    current_algo.inputs.append(inp)
                continue

            output_match = re.match(r'^(?:Output|Ensure)s?:\s*(.*)', sline, re.IGNORECASE)
            if output_match:
                outp = output_match.group(1).strip()
                if outp:
                    current_algo.outputs.append(outp)
                continue

            current_algo.pseudocode += line + "\n"

    if current_algo:
        algorithms.append(current_algo)

    return algorithms

def extract_sections(text: str) -> List[PaperSection]:
    """Reconstruct markdown sections based on numeric/title patterns."""
    sections = []

    # Common academic paper section headers:
    # 1. Introduction
    # I. Introduction
    # 2 Related Work
    header_pattern = re.compile(r'^\s*((?:\d+\.)+|[IVX]+\.)\s+([A-Z][A-Za-z\s]+)$', re.MULTILINE)

    matches = list(header_pattern.finditer(text))

    if not matches:
        # No clear sections, return one single section
        formulas = extract_formulas(text)
        algorithms = extract_algorithms(text)
        sections.append(PaperSection(
            title="Content",
            level=1,
            content=text,
            formulas=formulas,
            algorithms=algorithms
        ))
        return sections

    # Extract text before the first section
    intro_text = text[:matches[0].start()].strip()
    if intro_text:
        formulas = extract_formulas(intro_text)
        algorithms = extract_algorithms(intro_text)
        sections.append(PaperSection(
            title="Abstract/Intro",
            level=1,
            content=intro_text,
            formulas=formulas,
            algorithms=algorithms
        ))

    for i in range(len(matches)):
        start = matches[i].end()
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)

        section_title = matches[i].group(0).strip()
        section_content = text[start:end].strip()

        formulas = extract_formulas(section_content)
        algorithms = extract_algorithms(section_content)

        sections.append(PaperSection(
            title=section_title,
            level=1,
            content=section_content,
            formulas=formulas,
            algorithms=algorithms
        ))

    return sections

def extract_from_pdf(pdf_source: Union[str, bytes]) -> ParsedPaper:
    """
    Extract content from a PDF file or bytes using pypdf.
    Returns a ParsedPaper object.
    """
    if isinstance(pdf_source, bytes):
        file_obj = io.BytesIO(pdf_source)
    else:
        file_obj = open(pdf_source, 'rb')

    try:
        reader = PdfReader(file_obj)

        # Extract title from metadata if possible
        metadata = reader.metadata
        title = "Unknown Title"
        if metadata and metadata.title:
            title = metadata.title

        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n\n"

        full_text = clean_text(full_text)

        sections = extract_sections(full_text)

        parsed_paper = ParsedPaper(
            metadata=PaperMetadata(title=title),
            sections=sections,
            raw_markdown=full_text,
            source_type="local_pdf" if isinstance(pdf_source, str) else "bytes_pdf"
        )

        return parsed_paper
    finally:
        if isinstance(pdf_source, str):
            file_obj.close()
