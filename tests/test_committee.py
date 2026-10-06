import pytest
from paperagent.models import ParsedPaper, PaperMetadata, PaperSection
from paperagent.engine.committee import PeerReviewCommittee
from paperagent.engine.llm_client import LLMClient

@pytest.fixture
def sample_paper():
    metadata = PaperMetadata(
        title="Attention Is All You Need",
        authors=["Vaswani et al."],
        abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
        year=2017
    )
    section = PaperSection(
        title="Methodology",
        content="We propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism..."
    )
    return ParsedPaper(metadata=metadata, sections=[section])

def test_committee_review_fallback(sample_paper):
    """Test the fallback mode when LLMClient is in mock mode."""
    # Use mock client which will trigger fallback due to missing api keys / mock response not perfectly matching expected schema
    # (actually LLMClient's mock logic for structured generation uses schema, but we will ensure it gives a valid response or falls back)
    # The CommitteeReview schema is complex, LLMClient mock might generate it, but we can test the fallback directly or through evaluation
    committee = PeerReviewCommittee()
    
    # We will test evaluate_paper_committee
    result = committee.evaluate_paper_committee(sample_paper)
    
    # Check paper title
    assert result.paper_title == "Attention Is All You Need"
    
    # Check 3 reviewers
    assert len(result.reviews) == 3
    
    # Check diverse personas
    personas = [r.persona for r in result.reviews]
    assert any("Theory Expert" in p for p in personas)
    assert any("Empirical Skeptic" in p for p in personas)
    assert any("Impact Champion" in p for p in personas)
    
    # Check score bounds
    for review in result.reviews:
        assert 1 <= review.score <= 10
        assert review.reviewer_id
        
    # Check valid decision
    assert result.final_decision in ["Accept (Oral)", "Accept (Poster)", "Reject"]
    assert len(result.meta_review) > 0