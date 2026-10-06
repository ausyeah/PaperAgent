import pytest
from unittest.mock import MagicMock

from paperagent.models import ParsedPaper, PaperMetadata, PaperSection, PaperSemanticDiff, SemanticDiffItem
from paperagent.engine.semantic_diff import PaperSemanticDiffEngine, diff_papers
from paperagent.engine.llm_client import LLMClient

@pytest.fixture
def paper_v1():
    return ParsedPaper(
        metadata=PaperMetadata(
            title="A Novel Method for AI",
            authors=["Alice", "Bob"],
            year=2023,
            abstract="We propose a new method."
        ),
        sections=[
            PaperSection(title="Introduction", content="This is the intro."),
            PaperSection(title="Method", content="Here is our old method.")
        ]
    )

@pytest.fixture
def paper_v2():
    return ParsedPaper(
        metadata=PaperMetadata(
            title="A Novel Method for AI",
            authors=["Alice", "Bob"],
            year=2024,
            abstract="We propose an updated method."
        ),
        sections=[
            PaperSection(title="Introduction", content="This is the updated intro."),
            PaperSection(title="Method", content="Here is our new method with improvements."),
            PaperSection(title="Results", content="We beat SOTA.")
        ]
    )

def test_offline_diff_fallback(paper_v1, paper_v2):
    # Ensure offline mode by unsetting api keys
    mock_client = LLMClient()
    mock_client.gemini_api_key = None
    mock_client.openai_api_key = None

    engine = PaperSemanticDiffEngine(llm_client=mock_client)
    diff = engine.diff_papers(paper_v1, paper_v2)

    assert isinstance(diff, PaperSemanticDiff)
    assert diff.paper_title == "A Novel Method for AI"
    assert diff.v1_identifier == "v1"
    assert diff.v2_identifier == "v2"
    assert "Offline fallback" in diff.executive_diff_summary

    diff_types = {item.section_title: item.change_type for item in diff.diff_items}
    
    assert "Results" in diff_types
    assert diff_types["Results"] == "added"

    assert "Method" in diff_types
    assert diff_types["Method"] == "modified"

    assert "Introduction" in diff_types
    assert diff_types["Introduction"] == "modified"

def test_llm_diff(paper_v1, paper_v2, monkeypatch):
    mock_client = LLMClient()
    mock_client.gemini_api_key = "fake_key"
    
    expected_diff = PaperSemanticDiff(
        paper_title="A Novel Method for AI",
        diff_items=[
            SemanticDiffItem(section_title="Introduction", change_type="modified", v1_summary="old intro", v2_summary="new intro"),
            SemanticDiffItem(section_title="Method", change_type="modified", v1_summary="old method", v2_summary="new method"),
            SemanticDiffItem(section_title="Results", change_type="added", v1_summary="", v2_summary="We beat SOTA.")
        ],
        executive_diff_summary="v2 added results and updated method."
    )
    
    mock_client.generate_structured = MagicMock(return_value=expected_diff)

    engine = PaperSemanticDiffEngine(llm_client=mock_client)
    diff = engine.diff_papers(paper_v1, paper_v2)

    assert isinstance(diff, PaperSemanticDiff)
    assert diff.paper_title == "A Novel Method for AI"
    assert len(diff.diff_items) == 3
    assert diff.executive_diff_summary == "v2 added results and updated method."
    mock_client.generate_structured.assert_called_once()

def test_convenience_function(paper_v1, paper_v2):
    mock_client = LLMClient()
    mock_client.gemini_api_key = None
    mock_client.openai_api_key = None
    
    diff = diff_papers(paper_v1, paper_v2, mock_client)
    assert isinstance(diff, PaperSemanticDiff)