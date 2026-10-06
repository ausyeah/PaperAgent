import pytest
from unittest.mock import MagicMock
from paperagent.models import (
    PaperProject, 
    ParsedPaper, 
    PaperMetadata, 
    OpenReviewReport,
    AnalysisReport,
    ReviewerCritique,
    RebuttalLetter,
    RebuttalPoint
)
from paperagent.engine.rebuttal import AuthorRebuttalDrafter
from paperagent.engine.llm_client import LLMClient

@pytest.fixture
def dummy_project():
    return PaperProject(
        id="test-proj-1",
        paper=ParsedPaper(
            metadata=PaperMetadata(title="Test Paper", authors=["Alice", "Bob"], year=2023),
            sections=[],
            raw_markdown="Content",
            source_type="arxiv"
        ),
        analysis=AnalysisReport(
            executive_summary="Summary",
            core_problem="Problem",
            key_innovation="Innovation",
            methodology_overview="Methodology",
            reviewer_critique=ReviewerCritique(
                weaknesses=["Missing baseline A", "Unclear notation in Eq 3"]
            )
        )
    )

@pytest.fixture
def dummy_review():
    return OpenReviewReport(
        paper_title="Test Paper",
        summary_of_work="Good work",
        weaknesses=["Needs more ablation studies", "Limited dataset diversity"]
    )

def test_draft_with_review(dummy_project, dummy_review):
    client = MagicMock(spec=LLMClient)
    expected_rebuttal = RebuttalLetter(
        paper_title="Test Paper",
        overall_strategy="Adding ablations and more datasets",
        points=[
            RebuttalPoint(
                reviewer_id="Reviewer 1",
                critique_summary="Needs more ablation studies",
                response_strategy="Additional Experiment",
                detailed_rebuttal="We added ablations in Appendix B.",
                proposed_new_experiments=["Ablation X"]
            )
        ],
        markdown_letter="Dear Reviewers..."
    )
    client.generate_structured.return_value = expected_rebuttal
    
    drafter = AuthorRebuttalDrafter()
    rebuttal = drafter.draft_author_rebuttal(dummy_project, review=dummy_review, client=client)
    
    assert rebuttal.paper_title == "Test Paper"
    assert len(rebuttal.points) == 1
    assert rebuttal.points[0].critique_summary == "Needs more ablation studies"
    client.generate_structured.assert_called_once()
    call_args = client.generate_structured.call_args[1]
    assert "Needs more ablation studies" in call_args["prompt"]
    assert "Limited dataset diversity" in call_args["prompt"]

def test_fallback_to_project_analysis(dummy_project):
    client = MagicMock(spec=LLMClient)
    expected_rebuttal = RebuttalLetter(
        paper_title="Test Paper",
        overall_strategy="Address missing baselines",
        points=[
            RebuttalPoint(
                reviewer_id="Reviewer 1",
                critique_summary="Missing baseline A",
                response_strategy="Additional Experiment",
                detailed_rebuttal="We added baseline A.",
                proposed_new_experiments=["Baseline A"]
            )
        ],
        markdown_letter="Dear Reviewers..."
    )
    client.generate_structured.return_value = expected_rebuttal
    
    drafter = AuthorRebuttalDrafter()
    rebuttal = drafter.draft_author_rebuttal(dummy_project, review=None, client=client)
    
    assert rebuttal.paper_title == "Test Paper"
    client.generate_structured.assert_called_once()
    call_args = client.generate_structured.call_args[1]
    assert "Missing baseline A" in call_args["prompt"]
    assert "Unclear notation in Eq 3" in call_args["prompt"]

def test_offline_fallback(dummy_project, dummy_review):
    client = MagicMock(spec=LLMClient)
    # Simulate API failure
    client.generate_structured.side_effect = Exception("API offline")
    
    drafter = AuthorRebuttalDrafter()
    rebuttal = drafter.draft_author_rebuttal(dummy_project, review=dummy_review, client=client)
    
    # Should fall back to dummy review's weaknesses
    assert rebuttal.paper_title == "Test Paper"
    assert len(rebuttal.points) == 2
    assert "Needs more ablation studies" in rebuttal.points[0].detailed_rebuttal
    assert "Needs more ablation studies" in rebuttal.markdown_letter