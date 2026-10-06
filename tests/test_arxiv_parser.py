import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
import urllib.error

from paperagent.parser.arxiv import extract_arxiv_id, fetch_arxiv_metadata, download_arxiv_pdf
from paperagent.models import PaperMetadata

def test_extract_arxiv_id_pure_ids():
    assert extract_arxiv_id("2312.12456") == "2312.12456"
    assert extract_arxiv_id("2312.12456v2") == "2312.12456v2"
    assert extract_arxiv_id("math/0501001") == "math/0501001"
    assert extract_arxiv_id("math.AG/0501001v2") == "math.AG/0501001v2"

def test_extract_arxiv_id_urls():
    assert extract_arxiv_id("https://arxiv.org/abs/2312.12456") == "2312.12456"
    assert extract_arxiv_id("http://arxiv.org/abs/2312.12456v2") == "2312.12456v2"
    assert extract_arxiv_id("https://arxiv.org/pdf/2312.12456.pdf") == "2312.12456"
    assert extract_arxiv_id("https://arxiv.org/pdf/math.AG/0501001v2.pdf") == "math.AG/0501001v2"
    assert extract_arxiv_id("https://arxiv.org/html/2312.12456v1") == "2312.12456v1"

def test_extract_arxiv_id_invalid():
    assert extract_arxiv_id("not an arxiv id") is None
    assert extract_arxiv_id("https://google.com") is None

MOCK_XML_RESPONSE = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2312.12456v1</id>
    <updated>2023-12-19T18:00:00Z</updated>
    <published>2023-12-19T18:00:00Z</published>
    <title>A Great Paper on Something</title>
    <summary>
      This is a great paper.
      It solves many problems.
    </summary>
    <author>
      <name>John Doe</name>
    </author>
    <author>
      <name>Jane Smith</name>
    </author>
    <arxiv:doi xmlns:arxiv="http://arxiv.org/schemas/atom">10.1234/test</arxiv:doi>
    <link href="http://arxiv.org/abs/2312.12456v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/2312.12456v1" rel="related" type="application/pdf"/>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>
"""

@patch('urllib.request.urlopen')
def test_fetch_arxiv_metadata_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = MOCK_XML_RESPONSE
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    metadata = fetch_arxiv_metadata("2312.12456")

    assert isinstance(metadata, PaperMetadata)
    assert metadata.title == "A Great Paper on Something"
    assert metadata.abstract == "This is a great paper.       It solves many problems."
    assert metadata.authors == ["John Doe", "Jane Smith"]
    assert metadata.year == 2023
    assert metadata.doi == "10.1234/test"
    assert metadata.categories == ["cs.AI", "cs.LG"]
    assert metadata.pdf_url == "http://arxiv.org/pdf/2312.12456v1"
    assert metadata.arxiv_id == "2312.12456"

@patch('urllib.request.urlopen')
def test_fetch_arxiv_metadata_no_entry(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = b"""<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>"""
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    with pytest.raises(ValueError, match="No results found"):
        fetch_arxiv_metadata("0000.0000")

@patch('urllib.request.urlopen')
def test_fetch_arxiv_metadata_api_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError("Network Error")

    with pytest.raises(ValueError, match="Failed to fetch metadata"):
        fetch_arxiv_metadata("2312.12456")

@patch('urllib.request.urlretrieve')
def test_download_arxiv_pdf_with_path(mock_urlretrieve):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        output_path = tmp.name

    try:
        # Mock successful download
        mock_urlretrieve.return_value = (output_path, None)

        saved_path = download_arxiv_pdf("2312.12456", output_path)

        assert saved_path == output_path
        import pathlib
        mock_urlretrieve.assert_called_once_with(
            "https://arxiv.org/pdf/2312.12456.pdf",
            pathlib.Path(output_path)
        )
    finally:
        os.remove(output_path)

@patch('urllib.request.urlretrieve')
def test_download_arxiv_pdf_without_path(mock_urlretrieve, monkeypatch):
    from paperagent.config import settings

    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock settings.cache_dir
        monkeypatch.setattr(settings, 'cache_dir', MagicMock())
        settings.cache_dir.__truediv__.return_value = os.path.join(tmpdir, "2312.12456.pdf")

        # Test download without explicit output_path
        saved_path = download_arxiv_pdf("2312.12456")

        assert saved_path == os.path.join(tmpdir, "2312.12456.pdf")
        mock_urlretrieve.assert_called_once()
