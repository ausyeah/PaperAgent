import pytest
from unittest.mock import MagicMock
from paperagent.engine.hypothesis import ScientificHypothesisGenerator, generate_hypotheses
from paperagent.engine.llm_client import LLMClient
from paperagent.models import ParsedPaper, PaperMetadata, PaperSection, HypothesisCollection, ResearchHypothesis
from pydantic import ValidationError

@pytest.fixture
def mock_paper():
    return ParsedPaper(
        metadata=PaperMetadata(
            title="Attention Is All You Need",
            abstract="We propose a new simple network architecture, the Transformer.",
            authors=["Vaswani et al."],
            year=2017
        ),
        sections=[
            PaperSection(title="Introduction", content="RNNs are slow."),
            PaperSection(title="Model Architecture", content="Self-attention rules.")
        ]
    )

def test_offline_fallback(mock_paper):
    generator = ScientificHypothesisGenerator()
    
    # Passing a dummy client that raises an exception to trigger the fallback
    class BrokenClient:
        def generate_structured(self, *args, **kwargs):
            raise Exception("LLM is down")
            
    collection = generator.generate_hypotheses(mock_paper, client=BrokenClient())
    
    assert isinstance(collection, HypothesisCollection)
    assert collection.paper_title == "Attention Is All You Need"
    assert 3 <= len(collection.hypotheses) <= 5
    
    for hyp in collection.hypotheses:
        assert isinstance(hyp, ResearchHypothesis)
        assert hyp.title
        assert hyp.rationale
        assert hyp.proposed_modification
        assert hyp.expected_gain
        assert 0.0 <= hyp.feasibility_score <= 1.0
        assert hyp.validation_protocol

def test_llm_success(mock_paper):
    # Setup mock LLM Client
    mock_collection = HypothesisCollection(
        paper_title="Attention Is All You Need",
        hypotheses=[
            ResearchHypothesis(
                hypothesis_id="hyp-1",
                title="Mock Hyp",
                rationale="Mock Rationale",
                proposed_modification="Mock Mod",
                expected_gain="Mock Gain",
                feasibility_score=0.9,
                validation_protocol="Mock Protocol"
            )
        ],
        strategic_summary="Mock Summary"
    )
    
    class MockClient:
        def generate_structured(self, prompt, response_model, system_prompt):
            return mock_collection
            
    generator = ScientificHypothesisGenerator()
    collection = generator.generate_hypotheses(mock_paper, client=MockClient())
    
    assert len(collection.hypotheses) == 1
    assert collection.hypotheses[0].title == "Mock Hyp"
    assert collection.strategic_summary == "Mock Summary"

def test_feasibility_bounds_validation():
    # If the LLM tries to instantiate with an out-of-bounds feasibility score, Pydantic should catch it.
    with pytest.raises(ValidationError):
        ResearchHypothesis(
            hypothesis_id="hyp-1",
            title="Bad Hyp 1",
            rationale="R", proposed_modification="M", expected_gain="G",
            feasibility_score=1.5, # Out of bounds
            validation_protocol="V"
        )
    with pytest.raises(ValidationError):
        ResearchHypothesis(
            hypothesis_id="hyp-2",
            title="Bad Hyp 2",
            rationale="R", proposed_modification="M", expected_gain="G",
            feasibility_score=-0.5, # Out of bounds
            validation_protocol="V"
        )

def test_generate_hypotheses_helper(mock_paper):
    class BrokenClient:
        def generate_structured(self, *args, **kwargs):
            raise Exception("LLM is down")
            
    collection = generate_hypotheses(mock_paper, client=BrokenClient())
    assert isinstance(collection, HypothesisCollection)
    assert len(collection.hypotheses) >= 3