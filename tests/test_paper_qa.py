import pytest
from datetime import datetime
from unittest.mock import MagicMock

from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, PaperSection, ExtractedFormula, QAResponse
from paperagent.engine.paper_qa import PaperQAAgent

@pytest.fixture
def mock_project():
    metadata = PaperMetadata(title="Test Paper", authors=["A. Author"], year=2023)
    formulas = [
        ExtractedFormula(
            id="f1", 
            latex="E = mc^2", 
            context_text="Energy equation",
            inline=False,
            confidence=0.9,
            section="Introduction"
        )
    ]
    sections = [
        PaperSection(
            title="Introduction",
            content="This is a paper about relativity. Energy equals mass times the speed of light squared.",
            formulas=formulas
        )
    ]
    paper = ParsedPaper(metadata=metadata, sections=sections, source_type="pdf")
    return PaperProject(id="test_id", paper=paper)

def test_paper_qa_offline_fallback(mock_project):
    """Test the offline keyword overlap fallback."""
    mock_llm_client = MagicMock()
    mock_llm_client.gemini_api_key = None
    mock_llm_client.openai_api_key = None

    agent = PaperQAAgent(llm_client=mock_llm_client)
    
    query = "What is this paper about?"
    response = agent.answer_question(query, mock_project)
    
    assert isinstance(response, QAResponse)
    assert response.query == query
    assert len(response.citations) > 0
    assert response.citations[0].section_title == "Introduction"
    assert "This is a paper about relativity" in response.citations[0].relevant_quote
    assert response.confidence_score > 0.0

def test_paper_qa_llm_call(mock_project):
    """Test QA when LLM is available."""
    mock_llm_client = MagicMock()
    mock_llm_client.gemini_api_key = "fake_key"
    mock_llm_client.generate_structured.return_value = QAResponse(
        query="What is the energy equation?",
        answer="The energy equation is E = mc^2.",
        citations=[],
        confidence_score=0.95
    )

    agent = PaperQAAgent(llm_client=mock_llm_client)
    
    query = "What is the energy equation?"
    response = agent.answer_question(query, mock_project)
    
    assert isinstance(response, QAResponse)
    assert response.query == query
    assert response.answer == "The energy equation is E = mc^2."
    assert response.confidence_score == 0.95
    mock_llm_client.generate_structured.assert_called_once()