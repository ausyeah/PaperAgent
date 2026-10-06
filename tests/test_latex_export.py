import os
import zipfile
import pytest
from paperagent.models import (
    PaperProject, ParsedPaper, PaperMetadata, PaperSection,
    AnalysisReport, FormulaExplanation, ReviewerCritique,
    SynthesisResult
)
from paperagent.export.latex import generate_latex_source, generate_bibtex, export_latex_bundle

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

def test_generate_latex_source(mock_project):
    latex = generate_latex_source(mock_project)

    # Check Packages
    assert r"\usepackage{amsmath}" in latex
    assert r"\usepackage{algorithm}" in latex
    assert r"\usepackage{algpseudocode}" in latex
    assert r"\usepackage{listings}" in latex
    assert r"\usepackage{hyperref}" in latex
    assert r"\usepackage{booktabs}" in latex

    # Check Metadata
    assert r"\title{Attention Is All You Need}" in latex
    assert r"\author{Ashish Vaswani, Noam Shazeer}" in latex
    assert "We propose a new simple network architecture, the Transformer." in latex

    # Check Sections
    assert r"\section{Executive Summary}" in latex
    assert "Replaces RNNs with attention." in latex

    assert r"\section{Mathematical Formulation}" in latex
    assert r"Attention(Q, K, V) = softmax(\frac{QK^T}{\sqrt{d_k}})V" in latex

    assert r"\section{Extracted Algorithm}" in latex
    assert "Algorithm Name: Scaled Dot-Product Attention" in latex

    assert r"\section{Python Implementation Code}" in latex
    assert r"\begin{lstlisting}[language=Python]" in latex
    assert "def attention(q, k, v):" in latex

    assert r"\section{Peer Review}" in latex
    assert "Overall Score:" in latex
    assert "9/10" in latex

def test_export_latex_bundle(mock_project, tmp_path):
    output_zip = os.path.join(tmp_path, "export.zip")
    zip_path = export_latex_bundle(mock_project, output_zip)

    assert os.path.exists(zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        namelist = zipf.namelist()
        assert "main.tex" in namelist
        assert "references.bib" in namelist
        assert "README.md" in namelist
        assert "reproduction.py" in namelist

        main_tex = zipf.read("main.tex").decode('utf-8')
        assert r"\documentclass{article}" in main_tex

        readme = zipf.read("README.md").decode('utf-8')
        assert "Attention Is All You Need" in readme
        assert "Overleaf Instructions" in readme

        reproduction = zipf.read("reproduction.py").decode('utf-8')
        assert "def attention(q, k, v):" in reproduction
