import pytest
from unittest.mock import MagicMock
from paperagent.models import ParsedPaper, PaperMetadata, PaperSection, ReproducibilityScorecard
from paperagent.engine.scorecard import ReproducibilityEvaluator, evaluate_reproducibility

@pytest.fixture
def mock_paper():
    return ParsedPaper(
        metadata=PaperMetadata(
            title="Attention Is All You Need",
            authors=["Vaswani et al."],
            abstract="We propose the Transformer."
        ),
        sections=[
            PaperSection(
                title="Implementation Details",
                content="Our code is available at https://github.com/tensorflow/tensor2tensor. "
                        "We trained on 8 NVIDIA P100 GPUs for 3.5 days. Learning rate was 0.0001, batch size 256. "
                        "We report standard deviation across 5 random seeds (seed=42). "
                        "The WMT 2014 English-German dataset was used with an open license. "
                        "Model checkpoints are released at huggingface.co/transformer. "
                        "We follow standard evaluation protocol and provide mathematical proofs in Section 3."
            )
        ]
    )

def test_scorecard_offline_evaluation(mock_paper):
    evaluator = ReproducibilityEvaluator()
    scorecard = evaluator._evaluate_offline(mock_paper, mock_paper.sections[0].content)

    assert isinstance(scorecard, ReproducibilityScorecard)
    assert scorecard.paper_title == "Attention Is All You Need"
    assert scorecard.score == 100
    assert scorecard.verdict_level == "High Reproducibility"
    assert len(scorecard.criteria_checklist) == 10
    assert len(scorecard.improvement_recommendations) == 0

def test_scorecard_partial_offline(mock_paper):
    evaluator = ReproducibilityEvaluator()
    scorecard = evaluator._evaluate_offline(mock_paper, "A purely conceptual paper with no code.")

    assert scorecard.score < 50
    assert scorecard.verdict_level == "Low Reproducibility"
    assert len(scorecard.improvement_recommendations) > 0

def test_scorecard_with_mock_llm(mock_paper):
    mock_client = MagicMock()
    mock_scorecard = ReproducibilityScorecard(
        paper_title="Attention Is All You Need",
        score=90,
        criteria_checklist={"Code Repository URL Provided": True},
        verdict_level="High Reproducibility",
        improvement_recommendations=[]
    )
    mock_client.generate_structured.return_value = mock_scorecard

    res = evaluate_reproducibility(mock_paper, client=mock_client)
    assert res.score == 90
    assert res.paper_title == "Attention Is All You Need"
