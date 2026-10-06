import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, MetaAnalysisReport, ConsensusClaim
from paperagent.engine.meta_analysis import MetaAnalysisEngine
from paperagent.engine.llm_client import LLMClient


@pytest.fixture
def mock_projects():
    project1 = PaperProject(
        id="proj-1",
        paper=ParsedPaper(
            metadata=PaperMetadata(
                title="Paper A",
                abstract="We propose Method X which improves performance by 20%."
            )
        )
    )
    project2 = PaperProject(
        id="proj-2",
        paper=ParsedPaper(
            metadata=PaperMetadata(
                title="Paper B",
                abstract="We find that Method X only works on small datasets and degrades on large ones."
            )
        )
    )
    return [project1, project2]


def test_meta_analysis_engine_fallback(mock_projects):
    """Test the offline fallback behavior of MetaAnalysisEngine."""
    client = LLMClient()
    client.gemini_api_key = None
    client.openai_api_key = None
    
    engine = MetaAnalysisEngine(llm_client=client)
    report = engine.analyze_multi_paper_consensus(topic="Method X Performance", projects=mock_projects)
    
    assert isinstance(report, MetaAnalysisReport)
    assert report.topic == "Method X Performance"
    assert "Paper A" in report.analyzed_papers
    assert "Paper B" in report.analyzed_papers
    assert len(report.claims) == 1
    assert report.claims[0].consensus_verdict == "contested"
    assert "Mock claim" in report.claims[0].claim
    assert "Paper A" in report.claims[0].supporting_papers


def test_meta_analysis_engine_insufficient_papers():
    """Test that meta-analysis raises ValueError when given < 2 papers."""
    engine = MetaAnalysisEngine()
    with pytest.raises(ValueError, match="Meta-analysis requires at least 2 papers."):
        engine.analyze_multi_paper_consensus(topic="Test", projects=[])


def test_meta_analysis_engine_llm_success(mock_projects):
    """Test successful LLM generation of MetaAnalysisReport."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.gemini_api_key = "dummy"
    
    expected_report = MetaAnalysisReport(
        topic="Method X Performance",
        analyzed_papers=["Paper A", "Paper B"],
        claims=[
            ConsensusClaim(
                claim="Method X improves performance",
                supporting_papers=["Paper A"],
                opposing_papers=["Paper B"],
                consensus_verdict="contested",
                nuance_analysis="Depends on dataset size."
            )
        ],
        overall_consensus_summary="Method X is controversial."
    )
    
    mock_client.generate_structured.return_value = expected_report
    
    engine = MetaAnalysisEngine(llm_client=mock_client)
    report = engine.analyze_multi_paper_consensus(topic="Method X Performance", projects=mock_projects)
    
    assert report == expected_report
    mock_client.generate_structured.assert_called_once()
    assert "Method X Performance" in mock_client.generate_structured.call_args[1]["prompt"]


def test_meta_analysis_engine_llm_error_fallback(mock_projects):
    """Test fallback when LLM generation raises an exception."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.gemini_api_key = "dummy"
    
    mock_client.generate_structured.side_effect = Exception("API Error")
    
    engine = MetaAnalysisEngine(llm_client=mock_client)
    report = engine.analyze_multi_paper_consensus(topic="Test Topic", projects=mock_projects)
    
    assert isinstance(report, MetaAnalysisReport)
    assert report.topic == "Test Topic"
    assert report.claims[0].consensus_verdict == "insufficient_evidence"
    assert "API Error" in report.claims[0].claim
