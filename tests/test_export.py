import json
import pytest
from datetime import datetime, timezone
from paperagent.models import (
    PaperProject, ParsedPaper, PaperMetadata, PaperSection,
    AnalysisReport, FormulaExplanation, ReviewerCritique,
    SynthesisResult
)
from paperagent.export import export_markdown, export_jupyter_notebook, generate_bibtex

@pytest.fixture
def mock_project():
    meta = PaperMetadata(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        abstract="We propose a new simple network architecture, the Transformer.",
        year=2017,
        arxiv_id="1706.03762"
    )

    sections = [
        PaperSection(title="Introduction", content="Recurrent neural networks...")
    ]

    paper = ParsedPaper(metadata=meta, sections=sections, source_type="arxiv")

    critique = ReviewerCritique(
        strengths=["Highly parallelizable"],
        weaknesses=["Requires large datasets"],
        boundary_conditions=["Not for small data"],
        potential_reproducibility_pitfalls=["Hyperparameter tuning"],
        score=9
    )

    formula = FormulaExplanation(
        formula_id="eq-1",
        latex=r"Attention(Q, K, V) = softmax(\frac{QK^T}{\sqrt{d_k}})V",
        intuitive_intuition="Computes weights based on query-key similarity.",
        variable_glossary={"Q": "Queries", "K": "Keys", "V": "Values"},
        step_by_step_breakdown=["Compute dot product", "Scale", "Softmax", "Multiply by V"]
    )

    analysis = AnalysisReport(
        executive_summary="Replaces RNNs with attention.",
        core_problem="Sequential computation in RNNs.",
        key_innovation="Self-attention mechanism.",
        methodology_overview="Encoder-decoder structure using multi-head attention.",
        formula_explanations=[formula],
        reviewer_critique=critique
    )

    synthesis = SynthesisResult(
        algorithm_name="Scaled Dot-Product Attention",
        target_module_code="def attention(q, k, v):\n    pass",
        test_suite_code="def test_attention():\n    assert True",
        toy_benchmark_code="if __name__ == '__main__':\n    print('Run')"
    )

    return PaperProject(
        id="proj-123",
        paper=paper,
        analysis=analysis,
        synthesis=synthesis
    )

def test_export_markdown(mock_project):
    markdown = export_markdown(mock_project)

    # Check Metadata
    assert "# Attention Is All You Need" in markdown
    assert "**Authors:** Ashish Vaswani, Noam Shazeer" in markdown
    assert "## Abstract" in markdown

    # Check Analysis
    assert "## Executive Summary" in markdown
    assert "Replaces RNNs with attention." in markdown

    # Check Formulas
    assert "## Formula Demystification Cards" in markdown
    assert "Attention(Q, K, V)" in markdown

    # Check Critique
    assert "## NeurIPS Reviewer Critique" in markdown
    assert "**Score:** 9/10" in markdown

    # Check Synthesis
    assert "## Synthesized Algorithm" in markdown
    assert "def attention(q, k, v):" in markdown

def test_export_jupyter_notebook(mock_project):
    notebook_json = export_jupyter_notebook(mock_project)

    # Ensure valid JSON
    notebook = json.loads(notebook_json)

    assert "cells" in notebook
    assert "metadata" in notebook
    assert notebook["nbformat"] == 4

    cells = notebook["cells"]
    assert len(cells) > 0

    # Verify we have both markdown and code cells
    cell_types = [cell["cell_type"] for cell in cells]
    assert "markdown" in cell_types
    assert "code" in cell_types

    # Check if specific code is present
    sources = ["".join(cell["source"]) for cell in cells]
    code_found = any("def attention(q, k, v):" in src for src in sources)
    assert code_found

def test_generate_bibtex():
    meta = PaperMetadata(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        year=2017,
        arxiv_id="1706.03762"
    )

    bibtex = generate_bibtex(meta)

    assert "@article{vaswani2017attention," in bibtex
    assert "title={Attention Is All You Need}" in bibtex
    assert "author={Ashish Vaswani and Noam Shazeer}" in bibtex
    assert "year={2017}" in bibtex
    assert "journal={arXiv preprint arXiv:1706.03762}" in bibtex
