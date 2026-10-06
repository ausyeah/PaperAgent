import pytest
from unittest.mock import patch, MagicMock
from paperagent.parser.arxiv_html import (
    fetch_arxiv_html,
    parse_arxiv_html,
    extract_paper_from_arxiv_source
)
import httpx

MOCK_HTML = """
<!DOCTYPE html>
<html>
<head><title>Mock Paper Title</title></head>
<body>
    <h1 class="ltx_title">Mock Paper Title</h1>
    <div class="ltx_author">Alice Smith</div>
    <span class="author">Bob Jones</span>

    <div class="ltx_abstract">This is a mock abstract.</div>

    <section class="ltx_section">
        <h2 class="ltx_title">1. Introduction</h2>
        <p>This is the introduction paragraph.</p>
        <p>Here is another paragraph.</p>
    </section>

    <section class="ltx_section">
        <h2 class="ltx_title">2. Methods</h2>
        <p>Here is an equation:</p>
        <math class="ltx_Math" alttext="E=mc^2">E=mc^2</math>

        <div class="ltx_equation" alttext="y = mx + b">y = mx + b</div>
    </section>

    <figure class="ltx_algorithm">
        <figcaption>Algorithm 1: Mock Algo</figcaption>
        <p>Step 1: Do something.</p>
        <p>Step 2: Do something else.</p>
    </figure>
</body>
</html>
"""

def test_fetch_arxiv_html_success():
    with patch('httpx.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>HTML CONTENT</html>"
        mock_get.return_value = mock_response

        result = fetch_arxiv_html("2312.12456")
        assert result == "<html>HTML CONTENT</html>"

def test_fetch_arxiv_html_not_found():
    with patch('httpx.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = fetch_arxiv_html("2312.12456")
        assert result is None

def test_fetch_arxiv_html_request_error():
    with patch('httpx.get') as mock_get:
        mock_get.side_effect = httpx.RequestError("Mock Error")

        result = fetch_arxiv_html("2312.12456")
        assert result is None

def test_parse_arxiv_html():
    parsed = parse_arxiv_html(MOCK_HTML, "1234.56789")

    assert parsed.metadata.title == "Mock Paper Title"
    assert parsed.metadata.authors == ["Alice Smith", "Bob Jones"]
    assert parsed.metadata.abstract == "This is a mock abstract."
    assert parsed.metadata.arxiv_id == "1234.56789"
    assert parsed.source_type == "arxiv_html"

    assert len(parsed.sections) == 2
    assert parsed.sections[0].title == "1. Introduction"
    assert "This is the introduction paragraph." in parsed.sections[0].content

    assert len(parsed.sections[0].formulas) == 2
    assert parsed.sections[0].formulas[0].latex == "E=mc^2"
    assert parsed.sections[0].formulas[1].latex == "y = mx + b"

    assert len(parsed.sections[0].algorithms) == 1
    assert parsed.sections[0].algorithms[0].name == "Algorithm 1: Mock Algo"

def test_extract_paper_from_arxiv_source_html():
    with patch('paperagent.parser.arxiv_html.fetch_arxiv_html', return_value=MOCK_HTML) as mock_fetch:
        parsed = extract_paper_from_arxiv_source("https://arxiv.org/abs/2312.12456")
        mock_fetch.assert_called_once_with("2312.12456")
        assert parsed.metadata.title == "Mock Paper Title"
        assert parsed.source_type == "arxiv_html"

def test_extract_paper_from_arxiv_source_fallback():
    with patch('paperagent.parser.arxiv_html.fetch_arxiv_html', return_value=None):
        with patch('paperagent.parser.arxiv_html.parse_paper') as mock_parse_paper:
            mock_parse_paper.return_value = "Mock PDF ParsedPaper"
            parsed = extract_paper_from_arxiv_source("https://arxiv.org/abs/2312.12456")
            mock_parse_paper.assert_called_once_with("https://arxiv.org/abs/2312.12456")
            assert parsed == "Mock PDF ParsedPaper"

def test_extract_paper_invalid_source():
    with pytest.raises(ValueError, match="Could not extract valid ArXiv ID from"):
        extract_paper_from_arxiv_source("invalid_url")
