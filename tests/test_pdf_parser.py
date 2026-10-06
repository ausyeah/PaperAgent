import pytest
from pypdf import PdfWriter
import io
import os
from unittest.mock import patch

from paperagent.parser.pdf_extractor import extract_formulas, extract_algorithms, extract_sections, extract_from_pdf
from paperagent.parser.mineru_adapter import parse_with_mineru
from paperagent.parser import parse_paper

def create_mock_pdf_bytes(text_content):
    # pypdf can't easily generate PDFs with arbitrary text.
    # Usually reportlab or fpdf is used.
    # So for `extract_from_pdf` we can just patch `PdfReader` or `pypdf.PageObject.extract_text`.
    pass

def test_formula_extraction():
    text = r"""
    Here is an inline formula $E=mc^2$ and another one $a^2 + b^2 = c^2$.
    Then a display formula:
    $$
    f(x) = \int_0^\infty e^{-x} dx
    $$
    And a block:
    \[
    \sum_{i=1}^n i = \frac{n(n+1)}{2}
    \]
    And an env:
    \begin{equation}
    x = y
    \end{equation}
    """
    formulas = extract_formulas(text)
    assert len(formulas) == 5
    latex_list = [f.latex for f in formulas]
    assert r"E=mc^2" in latex_list
    assert r"a^2 + b^2 = c^2" in latex_list
    assert r"f(x) = \int_0^\infty e^{-x} dx" in latex_list
    assert r"\sum_{i=1}^n i = \frac{n(n+1)}{2}" in latex_list
    assert r"x = y" in latex_list

def test_algorithm_extraction():
    text = r"""
    Some text before the algorithm.

    Algorithm 1: Momentum Update
    Input: target network parameter $\xi$, online network parameter $\theta$
    Output: Updated $\xi$
    1: for each step do
    2:   $\xi \leftarrow m \xi + (1-m) \theta$
    3: end for

    3. Methodology
    Some next section text...
    """
    algorithms = extract_algorithms(text)
    assert len(algorithms) == 1
    algo = algorithms[0]
    assert algo.name == "Algorithm 1: Momentum Update"
    assert r"target network parameter $\xi$, online network parameter $\theta$" in algo.inputs[0]
    assert r"Updated $\xi$" in algo.outputs[0]
    assert "for each step do" in algo.pseudocode

def test_section_extraction():
    text = """
    Abstract
    This is an abstract.

    1. Introduction
    Welcome to the intro.

    2. Related Work
    Lots of related work here.

    3. Methodology
    We do things here.
    """
    sections = extract_sections(text)
    assert len(sections) == 4
    assert sections[0].title == "Abstract/Intro"
    assert "This is an abstract." in sections[0].content

    assert sections[1].title == "1. Introduction"
    assert "Welcome to the intro." in sections[1].content

    assert sections[2].title == "2. Related Work"
    assert "Lots of related work here." in sections[2].content

    assert sections[3].title == "3. Methodology"
    assert "We do things here." in sections[3].content

@patch("paperagent.parser.pdf_extractor.PdfReader")
def test_extract_from_pdf(mock_pdf_reader):
    mock_page = type('MockPage', (), {'extract_text': lambda self: "1. Introduction\nText in introduction."})()
    mock_reader_instance = type('MockReader', (), {
        'pages': [mock_page],
        'metadata': type('MockMeta', (), {'title': 'Test Paper'})()
    })()
    mock_pdf_reader.return_value = mock_reader_instance

    # We pass some dummy bytes
    parsed = extract_from_pdf(b"dummy pdf content")
    assert parsed.metadata.title == "Test Paper"
    assert parsed.source_type == "bytes_pdf"
    assert len(parsed.sections) == 1
    assert parsed.sections[0].title == "1. Introduction"

@patch("paperagent.parser.pdf_extractor.PdfReader")
def test_parse_paper_local_fallback(mock_pdf_reader, tmp_path):
    mock_page = type('MockPage', (), {'extract_text': lambda self: "Hello World"})()
    mock_reader_instance = type('MockReader', (), {
        'pages': [mock_page],
        'metadata': type('MockMeta', (), {'title': 'Test Paper'})()
    })()
    mock_pdf_reader.return_value = mock_reader_instance

    dummy_pdf = tmp_path / "dummy.pdf"
    dummy_pdf.write_text("fake pdf")

    # This should go through parse_paper -> parse_with_mineru -> extract_from_pdf
    parsed = parse_paper(str(dummy_pdf))
    assert parsed.metadata.title == "Test Paper"
    assert parsed.source_type == "local_pdf"
