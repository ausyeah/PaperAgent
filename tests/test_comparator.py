import pytest
from unittest.mock import AsyncMock, patch

from paperagent.models import (
    ParsedPaper,
    PaperMetadata,
    PaperSection,
    ComparisonMatrix,
    ComparisonDimension
)
from paperagent.engine.comparator import PaperComparator
from paperagent.engine.llm_client import LLMClient


@pytest.fixture
def mock_paper_a():
    return ParsedPaper(
        metadata=PaperMetadata(title="Paper A", authors=["Alice"]),
        sections=[PaperSection(title="Method", content="Method A")]
    )


@pytest.fixture
def mock_paper_b():
    return ParsedPaper(
        metadata=PaperMetadata(title="Paper B", authors=["Bob"]),
        sections=[PaperSection(title="Method", content="Method B")]
    )


def test_fallback_matrix(mock_paper_a, mock_paper_b):
    """Test that the fallback matrix is generated correctly when in mock mode."""
    # Ensure LLMClient is initialized without API keys
    llm_client = LLMClient()
    llm_client.gemini_api_key = None
    llm_client.openai_api_key = None

    comparator = PaperComparator(llm_client=llm_client)
    matrix = comparator.compare_papers_sync(mock_paper_a, mock_paper_b)

    assert isinstance(matrix, ComparisonMatrix)
    assert matrix.paper_a_title == "Paper A"
    assert matrix.paper_b_title == "Paper B"
    assert len(matrix.dimensions) == 5
    assert matrix.trade_off_summary != ""
    assert matrix.recommended_choice != ""


@pytest.mark.asyncio
@patch.object(LLMClient, 'generate_structured_async', new_callable=AsyncMock)
async def test_successful_llm_generation(mock_generate, mock_paper_a, mock_paper_b):
    """Test successful generation using the mocked LLM method."""
    mock_matrix = ComparisonMatrix(
        paper_a_title="Mocked A",
        paper_b_title="Mocked B",
        dimensions=[
            ComparisonDimension(
                name="Mock Dimension",
                paper_a_value="A",
                paper_b_value="B",
                comparative_analysis="Analysis"
            )
        ],
        trade_off_summary="Mock summary",
        recommended_choice="Mock choice"
    )
    mock_generate.return_value = mock_matrix

    llm_client = LLMClient()
    # Mocking API keys so it doesn't hit the fallback instantly
    llm_client.gemini_api_key = "fake_key"

    comparator = PaperComparator(llm_client=llm_client)
    matrix = await comparator.compare_papers(mock_paper_a, mock_paper_b)

    assert matrix.paper_a_title == "Paper A"  # The comparator enforces title matching
    assert matrix.paper_b_title == "Paper B"
    assert matrix.dimensions[0].name == "Mock Dimension"
    assert matrix.trade_off_summary == "Mock summary"


@pytest.mark.asyncio
@patch.object(LLMClient, 'generate_structured_async', new_callable=AsyncMock)
async def test_llm_exception_fallback(mock_generate, mock_paper_a, mock_paper_b):
    """Test that if the LLM generation raises an exception, the fallback is used."""
    mock_generate.side_effect = Exception("LLM failure")

    llm_client = LLMClient()
    llm_client.gemini_api_key = "fake_key"

    comparator = PaperComparator(llm_client=llm_client)
    matrix = await comparator.compare_papers(mock_paper_a, mock_paper_b)

    # Should fall back
    assert len(matrix.dimensions) == 5
    assert matrix.dimensions[0].name == "Inductive Bias & Core Approach"
