"""
Unit tests for the PaperAnalyzer module.
"""
import pytest
from typing import Type, Any
from pydantic import BaseModel

from paperagent.models import (
    ParsedPaper,
    PaperMetadata,
    PaperSection,
    ExtractedFormula,
    ReviewerCritique,
    AnalysisReport
)
from paperagent.engine.llm_client import LLMClient
from paperagent.engine.analyzer import PaperAnalyzer, ExecutiveSummaryResult

class MockLLMClient(LLMClient):
    """A mock LLM client for testing without making real API calls."""

    def __init__(self):
        super().__init__()
        self.structured_responses = []
        self.call_count = 0

    def generate_structured(self, prompt: str, response_model: Type[BaseModel], **kwargs: Any) -> BaseModel:
        self.call_count += 1

        # Determine the type of response needed based on the response_model
        if response_model.__name__ == "ExecutiveSummaryResult":
            return response_model(
                executive_summary="Mocked executive summary.",
                core_problem="Mocked core problem.",
                key_innovation="Mocked key innovation.",
                methodology_overview="Mocked methodology."
            )
        elif response_model.__name__ == "PartialFormulaExpl":
            return response_model(
                variable_glossary={"x": "input", "y": "output"},
                intuitive_intuition="Mocked intuitive intuition.",
                step_by_step_breakdown=["Step 1", "Step 2"]
            )
        elif response_model.__name__ == "ReviewerCritique":
            return response_model(
                strengths=["Strength 1"],
                weaknesses=["Weakness 1"],
                boundary_conditions=["Fails when x is 0"],
                potential_reproducibility_pitfalls=["Missing hyperparams"],
                score=8
            )
        else:
            raise ValueError(f"Unexpected response model: {response_model.__name__}")


@pytest.fixture
def mock_parsed_paper():
    metadata = PaperMetadata(title="Test Paper", authors=["Alice"], abstract="Test Abstract")

    formulas_sec1 = [
        ExtractedFormula(id="eq-1", latex="E=mc^2", context_text="Energy equation"),
        ExtractedFormula(id="eq-2", latex="F=ma", context_text="Force equation")
    ]
    formulas_sec2 = [
        ExtractedFormula(id="eq-3", latex="a^2+b^2=c^2", context_text="Pythagoras"),
        ExtractedFormula(id="eq-4", latex="V=IR", context_text="Ohm's law"),
        ExtractedFormula(id="eq-5", latex="P=IV", context_text="Power equation"),
        ExtractedFormula(id="eq-6", latex="v=u+at", context_text="Kinematics") # Should not be processed (top 5 limit)
    ]

    sections = [
        PaperSection(title="Introduction", content="Intro content", formulas=formulas_sec1),
        PaperSection(title="Methodology", content="Method content", formulas=formulas_sec2)
    ]

    return ParsedPaper(metadata=metadata, sections=sections, raw_markdown="")

@pytest.fixture
def empty_parsed_paper():
    metadata = PaperMetadata(title="Empty Paper", authors=[])
    return ParsedPaper(metadata=metadata, sections=[], raw_markdown="")


def test_analyzer_normal_behavior(mock_parsed_paper):
    llm_client = MockLLMClient()
    analyzer = PaperAnalyzer(llm_client=llm_client)

    report = analyzer.analyze(mock_parsed_paper)

    assert isinstance(report, AnalysisReport)
    assert report.executive_summary == "Mocked executive summary."
    assert report.core_problem == "Mocked core problem."
    assert report.key_innovation == "Mocked key innovation."
    assert report.methodology_overview == "Mocked methodology."

    # Check that exactly 5 formulas were processed (since the paper has 6)
    assert len(report.formula_explanations) == 5
    assert report.formula_explanations[0].formula_id == "eq-1"
    assert report.formula_explanations[0].variable_glossary == {"x": "input", "y": "output"}
    assert report.formula_explanations[0].intuitive_intuition == "Mocked intuitive intuition."

    # Check critique
    assert isinstance(report.reviewer_critique, ReviewerCritique)
    assert report.reviewer_critique.score == 8

    # Check LLM call count (1 summary + 5 formulas + 1 critique = 7 calls)
    assert llm_client.call_count == 7

def test_analyzer_empty_paper(empty_parsed_paper):
    llm_client = MockLLMClient()
    analyzer = PaperAnalyzer(llm_client=llm_client)

    report = analyzer.analyze(empty_parsed_paper)

    assert isinstance(report, AnalysisReport)
    assert report.executive_summary == "Mocked executive summary."
    assert len(report.formula_explanations) == 0
    assert report.reviewer_critique.score == 8

    # Check LLM call count (1 summary + 0 formulas + 1 critique = 2 calls)
    assert llm_client.call_count == 2
