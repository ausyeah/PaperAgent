import json
import os
import pytest
from datetime import datetime, timezone

from paperagent.models import (
    PaperProject, ParsedPaper, PaperMetadata, AnalysisReport,
    ReviewerCritique, SynthesisResult, BenchmarkEvaluationResult,
    FormulaExplanation
)
from paperagent.export.poster import AcademicPosterGenerator

@pytest.fixture
def mock_project():
    meta = PaperMetadata(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        year=2017
    )
    paper = ParsedPaper(metadata=meta, raw_markdown="# Attention")
    
    analysis = AnalysisReport(
        executive_summary="Executive Summary Text",
        core_problem="Sequence to sequence translation is slow.",
        key_innovation="Self-attention mechanism.",
        methodology_overview="Encoder-decoder transformer architecture.",
        formula_explanations=[
            FormulaExplanation(
                formula_id="f1",
                latex="\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V",
                intuitive_intuition="Computes context-aware representation.",
                step_by_step_breakdown=[],
                variable_glossary={}
            )
        ],
        reviewer_critique=ReviewerCritique(
            strengths=["Novel", "Fast"],
            weaknesses=["High memory usage on long sequences"],
            final_decision="Accept (Poster)"
        ),
        timestamp=datetime.now(timezone.utc)
    )
    
    synthesis = SynthesisResult(
        algorithm_name="Transformer",
        target_module_code="",
        test_suite_code="",
        synthesized_code=""
    )
    
    return PaperProject(
        id="test-proj",
        paper=paper,
        analysis=analysis,
        synthesis=synthesis
    )

def test_generate_poster_instantiation(mock_project):
    generator = AcademicPosterGenerator()
    bundle = generator.generate_poster(mock_project)
    
    assert bundle is not None
    assert bundle.paper_title == "Attention Is All You Need"
    assert bundle.authors == ["Ashish Vaswani", "Noam Shazeer"]

def test_generate_poster_html_structure(mock_project):
    generator = AcademicPosterGenerator()
    bundle = generator.generate_poster(mock_project)
    
    html = bundle.standalone_poster_html
    # Check title and authors
    assert "Attention Is All You Need" in html
    assert "Ashish Vaswani, Noam Shazeer" in html
    
    # Check section content
    assert "Motivation" in html
    assert "Sequence to sequence translation is slow." in html
    
    assert "Methodology" in html
    assert "Encoder-decoder transformer architecture." in html
    
    assert "Key Innovation" in html
    assert "Self-attention mechanism." in html
    
    # Check formulas
    assert "\\text{Attention}(Q, K, V)" in html
    assert "Computes context-aware representation." in html
    
    # Check conclusion
    assert "Executive Summary Text" in html

def test_generate_poster_file_export(mock_project, tmp_path):
    generator = AcademicPosterGenerator()
    out_file = str(tmp_path / "poster.html")
    
    bundle = generator.generate_poster(mock_project, output_path=out_file)
    
    assert os.path.exists(out_file)
    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Attention Is All You Need" in content