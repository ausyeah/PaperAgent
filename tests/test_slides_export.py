import os
import tempfile
import pytest
from datetime import datetime, timezone
from paperagent.models import (
    PaperProject, ParsedPaper, PaperMetadata, PaperSection, ExtractedFormula,
    ExtractedAlgorithm, AnalysisReport, FormulaExplanation, ReviewerCritique,
    SynthesisResult
)
from paperagent.export.slides import generate_marp_slides, export_slides_file

@pytest.fixture
def mock_project():
    metadata = PaperMetadata(
        title="Test Paper Title",
        authors=["Alice", "Bob"],
        abstract="Test abstract",
        year=2024
    )

    formula1 = ExtractedFormula(
        id="eq1",
        latex="E = mc^2",
        context_text="Energy mass equivalence.",
        plain_explanation="Energy is mass times speed of light squared."
    )

    algo1 = ExtractedAlgorithm(
        id="algo1",
        name="Test Algo",
        pseudocode="1: a = 1\n2: return a",
        inputs=["None"],
        outputs=["Int"]
    )

    section1 = PaperSection(
        title="Methodology",
        level=1,
        content="Methodology content...",
        formulas=[formula1],
        algorithms=[algo1]
    )

    parsed_paper = ParsedPaper(
        metadata=metadata,
        sections=[section1],
        raw_markdown="# Test Paper Title\n..."
    )

    formula_exp = FormulaExplanation(
        formula_id="eq1",
        latex="E = mc^2",
        variable_glossary={"E": "Energy", "m": "Mass", "c": "Speed of Light"},
        intuitive_intuition="Mass and energy are interchangeable."
    )

    reviewer_critique = ReviewerCritique(
        strengths=["Strong methodology."],
        weaknesses=["Missing baselines."],
        score=7
    )

    analysis = AnalysisReport(
        executive_summary="This paper solves a big problem.",
        core_problem="The fundamental problem is big.",
        key_innovation="The big trick.",
        methodology_overview="Systematic overview.",
        formula_explanations=[formula_exp],
        reviewer_critique=reviewer_critique,
        timestamp=datetime.now(timezone.utc)
    )

    synthesis = SynthesisResult(
        algorithm_name="Test Algo Code",
        target_module_code="def test_algo():\n    return 1",
        test_suite_code="def test_test_algo():\n    assert test_algo() == 1"
    )

    project = PaperProject(
        id="proj-123",
        created_at=datetime.now(timezone.utc),
        paper=parsed_paper,
        analysis=analysis,
        synthesis=synthesis
    )

    return project

def test_generate_marp_slides(mock_project):
    deck = generate_marp_slides(mock_project)

    assert deck.title == "Test Paper Title"
    assert deck.author == "PaperAgent AI"
    assert deck.slide_count == 7

    # Check frontmatter
    assert "marp: true" in deck.marp_markdown
    assert "theme: gaia" in deck.marp_markdown
    assert "paginate: true" in deck.marp_markdown
    assert "math: katex" in deck.marp_markdown

    # Check Slide 1 content
    assert "# Test Paper Title" in deck.marp_markdown
    assert "**Alice, Bob**" in deck.marp_markdown
    assert "![PaperAgent Badge](https://img.shields.io/badge/Generated_by-PaperAgent-blue)" in deck.marp_markdown

    # Check Slide 2 content
    assert "## Motivation & Executive Brief" in deck.marp_markdown
    assert "This paper solves a big problem." in deck.marp_markdown

    # Check Slide 3 content
    assert "## Core Mathematical Formulation" in deck.marp_markdown
    assert "$$\nE = mc^2\n$$" in deck.marp_markdown
    assert "Mass and energy are interchangeable." in deck.marp_markdown

    # Check Slide 4 content
    assert "## Algorithmic Innovation & Pseudocode" in deck.marp_markdown
    assert "```\n1: a = 1\n2: return a\n```" in deck.marp_markdown
    assert "Systematic overview." in deck.marp_markdown

    # Check Slide 5 content
    assert "## Python Reproduction Implementation" in deck.marp_markdown
    assert "```python\ndef test_algo():\n    return 1\n```" in deck.marp_markdown

    # Check Slide 6 content
    assert "## NeurIPS Reviewer Critique" in deck.marp_markdown
    assert "**Score**: 7/10" in deck.marp_markdown
    assert "- Strong methodology." in deck.marp_markdown
    assert "- Missing baselines." in deck.marp_markdown

    # Check Slide 7 content
    assert "## Conclusion & Key Takeaways" in deck.marp_markdown
    assert "The fundamental problem is big." in deck.marp_markdown

def test_export_slides_file(mock_project):
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "slides.md")
        returned_path = export_slides_file(mock_project, output_path)

        assert returned_path == output_path
        assert os.path.exists(output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "marp: true" in content
        assert "# Test Paper Title" in content
        assert "## Conclusion & Key Takeaways" in content
