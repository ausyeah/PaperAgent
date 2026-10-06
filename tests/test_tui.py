import pytest
from rich.panel import Panel
from rich.table import Table

from paperagent.models import (
    ParsedPaper,
    PaperMetadata,
    PaperSection,
    AnalysisReport,
    ReviewerCritique,
    ExtractedFormula,
    SynthesisResult,
    OpenReviewReport,
    PaperProject
)
from paperagent.tui import (
    render_header,
    render_paper_summary,
    render_analysis_view,
    render_formula_gallery,
    render_code_view,
    render_openreview_card
)

@pytest.fixture
def mock_paper():
    metadata = PaperMetadata(
        title="Test Paper",
        authors=["Alice", "Bob"],
        abstract="A test abstract",
        arxiv_id="1234.5678",
        year=2024
    )
    section1 = PaperSection(title="Introduction", level=1, content="Intro content")
    section2 = PaperSection(title="Methods", level=1, content="Methods content")

    return ParsedPaper(
        metadata=metadata,
        sections=[section1, section2],
        raw_markdown="# Test Paper\n..."
    )

@pytest.fixture
def mock_analysis():
    critique = ReviewerCritique(
        strengths=["Good math", "Clear writing"],
        weaknesses=["Small dataset"],
        score=8
    )
    return AnalysisReport(
        executive_summary="This is a summary",
        core_problem="The problem is hard",
        key_innovation="We solved it",
        methodology_overview="By doing this",
        reviewer_critique=critique
    )

@pytest.fixture
def mock_formulas():
    f1 = ExtractedFormula(
        id="eq-1",
        latex="E=mc^2",
        plain_explanation="Energy equals mass times the speed of light squared"
    )
    f2 = ExtractedFormula(
        id="eq-2",
        latex="a^2 + b^2 = c^2",
        context_text="Pythagorean theorem"
    )
    return [f1, f2]

@pytest.fixture
def mock_synthesis():
    return SynthesisResult(
        algorithm_name="Test Algo",
        target_module_code="def test():\n    return True",
        test_suite_code="def test_test():\n    assert test() == True"
    )

@pytest.fixture
def mock_review():
    return OpenReviewReport(
        paper_title="Test Paper",
        summary_of_work="Summary",
        strengths=["Strength 1"],
        weaknesses=["Weakness 1"],
        soundness_score=3,
        presentation_score=4,
        contribution_score=3,
        overall_recommendation=8,
        reproducibility_checklist_passed=True
    )

def test_render_header():
    panel = render_header()
    assert isinstance(panel, Panel)
    assert "Welcome" in panel.title

def test_render_paper_summary(mock_paper):
    panel = render_paper_summary(mock_paper)
    assert isinstance(panel, Panel)
    assert "Paper Summary" in panel.title
    assert isinstance(panel.renderable, Table)

def test_render_analysis_view(mock_analysis):
    panel = render_analysis_view(mock_analysis)
    assert isinstance(panel, Panel)
    assert "Analysis Report" in panel.title
    assert "Executive Summary:" in panel.renderable

def test_render_formula_gallery(mock_formulas):
    table = render_formula_gallery(mock_formulas)
    assert isinstance(table, Table)
    assert "Formula Gallery" in table.title
    assert len(table.columns) == 3

def test_render_code_view(mock_synthesis):
    panel = render_code_view(mock_synthesis)
    assert isinstance(panel, Panel)
    assert "Synthesized Code: Test Algo" in panel.title

def test_render_openreview_card(mock_review):
    panel = render_openreview_card(mock_review)
    assert isinstance(panel, Panel)
    assert "OpenReview: Test Paper" in panel.title
