import pytest
from pydantic import ValidationError

from paperagent.models import ParsedPaper, PaperMetadata, OpenReviewReport
from paperagent.engine.openreview import OpenReviewEvaluator
from paperagent.engine.llm_client import LLMClient

@pytest.fixture
def mock_paper():
    metadata = PaperMetadata(
        title="Attention is All You Need",
        authors=["Vaswani et al."],
        abstract="We propose the Transformer.",
        year=2017
    )
    return ParsedPaper(
        metadata=metadata,
        raw_markdown="# Attention is All You Need\n\nWe propose a novel network architecture..."
    )

def test_evaluate_paper_mock_mode(mock_paper):
    llm_client = LLMClient()
    # Ensure offline mode by overriding keys if they are set
    llm_client.gemini_api_key = None
    llm_client.openai_api_key = None

    evaluator = OpenReviewEvaluator(llm_client=llm_client)
    report = evaluator.evaluate_paper_sync(mock_paper)

    assert isinstance(report, OpenReviewReport)
    assert report.paper_title == "Attention is All You Need"
    assert len(report.strengths) > 0
    assert len(report.weaknesses) > 0
    assert 1 <= report.soundness_score <= 4
    assert 1 <= report.overall_recommendation <= 10

def test_score_bounds_validation():
    # Test soundness_score bounds
    with pytest.raises(ValidationError):
        OpenReviewReport(
            paper_title="Test Paper",
            summary_of_work="Test summary",
            strengths=["strength"],
            weaknesses=["weakness"],
            questions_for_authors=["question"],
            reproducibility_checklist_passed=True,
            soundness_score=5,  # Out of bounds
            presentation_score=3,
            contribution_score=3,
            overall_recommendation=6
        )

    with pytest.raises(ValidationError):
        OpenReviewReport(
            paper_title="Test Paper",
            summary_of_work="Test summary",
            strengths=["strength"],
            weaknesses=["weakness"],
            questions_for_authors=["question"],
            reproducibility_checklist_passed=True,
            soundness_score=3,
            presentation_score=3,
            contribution_score=3,
            overall_recommendation=11  # Out of bounds
        )

def test_evaluate_paper_sync(mock_paper):
    evaluator = OpenReviewEvaluator()
    evaluator.llm_client.gemini_api_key = None
    evaluator.llm_client.openai_api_key = None

    report = evaluator.evaluate_paper_sync(mock_paper)

    assert isinstance(report, OpenReviewReport)
    assert report.paper_title == "Attention is All You Need"
