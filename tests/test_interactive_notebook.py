import json
import os
import pytest
from datetime import datetime, timezone

from paperagent.models import (
    PaperProject,
    ParsedPaper,
    PaperMetadata,
    AnalysisReport,
    SynthesisResult,
    FormulaExplanation,
    ReviewerCritique
)
from paperagent.export.interactive_notebook import export_interactive_notebook

@pytest.fixture
def mock_project() -> PaperProject:
    metadata = PaperMetadata(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        abstract="We propose a new simple network architecture, the Transformer.",
        year=2017
    )
    paper = ParsedPaper(
        id="transformer-1",
        metadata=metadata,
        sections=[]
    )
    
    critique = ReviewerCritique(
        strengths=["strong results"],
        weaknesses=["resource heavy"],
        methodology_score=4,
        impact_score=5,
        reproducibility_score=3,
        clarity_score=4,
        confidence_score=5,
        overall_recommendation="accept"
    )

    analysis = AnalysisReport(
        executive_summary="Summary",
        core_problem="Sequence transduction without RNNs",
        key_innovation="Self-attention",
        methodology_overview="Overview",
        reviewer_critique=critique,
        formula_explanations=[
            FormulaExplanation(
                formula_id="attention",
                latex=r"\text{Attention}(Q, K, V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}})V",
                intuitive_intuition="Computes context-aware representations"
            )
        ]
    )

    synthesis = SynthesisResult(
        algorithm_name="Scaled Dot-Product Attention",
        target_module_code="def attention(q, k, v):\n    pass\n",
        test_suite_code="def test_attention():\n    pass\n"
    )

    return PaperProject(
        id="project-1",
        paper=paper,
        analysis=analysis,
        synthesis=synthesis,
        created_at=datetime.now(timezone.utc)
    )

def test_export_interactive_notebook_json_schema(mock_project):
    bundle = export_interactive_notebook(mock_project)
    assert bundle is not None
    
    nb_dict = json.loads(bundle.notebook_json)
    assert "cells" in nb_dict
    assert "metadata" in nb_dict
    assert nb_dict.get("nbformat") == 4
    assert nb_dict.get("nbformat_minor") == 4

def test_export_interactive_notebook_widget_imports(mock_project):
    bundle = export_interactive_notebook(mock_project)
    
    assert "sequence_length_slider" in bundle.widget_features
    assert "live_matplotlib_plot" in bundle.widget_features
    
    assert "ipywidgets as widgets" in bundle.notebook_json
    assert "matplotlib.pyplot as plt" in bundle.notebook_json
    assert "IntSlider" in bundle.notebook_json
    assert "widgets.interactive" in bundle.notebook_json

def test_export_interactive_notebook_file_creation(mock_project, tmp_path):
    output_file = tmp_path / "notebook.ipynb"
    bundle = export_interactive_notebook(mock_project, output_path=str(output_file))
    
    assert os.path.exists(str(output_file))
    assert bundle.file_path == str(output_file)
    
    with open(output_file, "r") as f:
        file_content = f.read()
    
    assert file_content == bundle.notebook_json
    assert "Attention Is All You Need" in file_content
    assert r"\text{Attention}(Q, K, V)" in file_content
    assert "def attention(q, k, v)" in file_content
