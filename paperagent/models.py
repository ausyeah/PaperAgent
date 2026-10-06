"""
PaperAgent Core Data Models
Unified schemas used across Parser, AI Engine, Synthesizer, Runner, and Web/CLI interfaces.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class PaperMetadata(BaseModel):
    """Metadata of an academic paper."""
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    abstract: str = Field(default="", description="Paper abstract")
    arxiv_id: Optional[str] = Field(default=None, description="ArXiv ID (e.g. '2312.12456')")
    doi: Optional[str] = Field(default=None, description="DOI identifier")
    year: Optional[int] = Field(default=None, description="Publication year")
    categories: List[str] = Field(default_factory=list, description="ArXiv primary / secondary categories")
    pdf_url: Optional[str] = Field(default=None, description="Direct URL to PDF")


class ExtractedFormula(BaseModel):
    """An extracted mathematical equation or formula."""
    id: str = Field(..., description="Unique formula identifier (e.g. 'eq-1')")
    latex: str = Field(..., description="LaTeX representation of the formula")
    context_text: str = Field(default="", description="Surrounding text or explanation from paper")
    plain_explanation: Optional[str] = Field(default=None, description="AI-generated plain language intuitive explanation")


class ExtractedAlgorithm(BaseModel):
    """An algorithm or pseudocode block extracted from the paper."""
    id: str = Field(..., description="Algorithm identifier (e.g. 'algo-1')")
    name: str = Field(..., description="Algorithm name or caption (e.g. 'Algorithm 1: Momentum Contrast')")
    pseudocode: str = Field(..., description="Raw pseudocode or algorithm text")
    inputs: List[str] = Field(default_factory=list, description="Inputs required by the algorithm")
    outputs: List[str] = Field(default_factory=list, description="Outputs produced")
    complexity: Optional[str] = Field(default=None, description="Time/space complexity if mentioned")


class PaperSection(BaseModel):
    """A structural section of the paper."""
    title: str = Field(..., description="Section heading")
    level: int = Field(default=1, description="Heading level (1=H1, 2=H2, etc.)")
    content: str = Field(default="", description="Text content in markdown format")
    formulas: List[ExtractedFormula] = Field(default_factory=list)
    algorithms: List[ExtractedAlgorithm] = Field(default_factory=list)


class ParsedPaper(BaseModel):
    """Complete structured representation of a parsed paper."""
    metadata: PaperMetadata
    sections: List[PaperSection] = Field(default_factory=list)
    raw_markdown: str = Field(default="", description="Full extracted text in clean Markdown")
    source_type: str = Field(default="pdf", description="'arxiv', 'local_pdf', or 'mineru'")


class FormulaExplanation(BaseModel):
    """Intuitive plain-language decomposition of a mathematical equation."""
    formula_id: str
    latex: str
    variable_glossary: Dict[str, str] = Field(default_factory=dict, description="Variables and their real-world meaning")
    intuitive_intuition: str = Field(..., description="Why this formula was designed this way")
    step_by_step_breakdown: List[str] = Field(default_factory=list)


class ReviewerCritique(BaseModel):
    """Top-tier conference (NeurIPS/ICLR) style critical review."""
    strengths: List[str] = Field(default_factory=list, description="Core novelties and solid empirical findings")
    weaknesses: List[str] = Field(default_factory=list, description="Hidden assumptions, unproven claims, missing baselines")
    boundary_conditions: List[str] = Field(default_factory=list, description="When does this algorithm fail or degrade?")
    potential_reproducibility_pitfalls: List[str] = Field(default_factory=list, description="Ambiguous implementation details")
    score: int = Field(default=6, ge=1, le=10, description="Overall recommendation score 1-10")


class AnalysisReport(BaseModel):
    """AI Deep-Reading Analysis Report."""
    executive_summary: str = Field(..., description="High-level 3-minute executive summary")
    core_problem: str = Field(..., description="What fundamental problem does this paper solve?")
    key_innovation: str = Field(..., description="The key trick / breakthrough insight")
    methodology_overview: str = Field(..., description="Systematic walk-through of the proposed method")
    formula_explanations: List[FormulaExplanation] = Field(default_factory=list)
    reviewer_critique: ReviewerCritique
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionResult(BaseModel):
    """Execution output from running the synthesized Python code."""
    success: bool
    exit_code: int
    stdout: str = Field(default="")
    stderr: str = Field(default="")
    execution_time_seconds: float = Field(default=0.0)
    generated_artifacts: List[str] = Field(default_factory=list, description="Paths to generated figures or output files")


class SynthesisResult(BaseModel):
    """Synthesized runnable Python code and tests for the paper's algorithm."""
    algorithm_name: str
    target_module_code: str = Field(..., description="Self-contained Python code implementing the core algorithm")
    test_suite_code: str = Field(..., description="PyTest verification suite with toy/synthetic data")
    toy_benchmark_code: Optional[str] = Field(default=None, description="Script to run a minimal benchmark or toy demonstration")
    execution_result: Optional[ExecutionResult] = Field(default=None)
    jupyter_notebook_json: Optional[str] = Field(default=None, description="Exportable .ipynb JSON string")


class PaperProject(BaseModel):
    """Complete PaperAgent workspace session project."""
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paper: ParsedPaper
    analysis: Optional[AnalysisReport] = Field(default=None)
    synthesis: Optional[SynthesisResult] = Field(default=None)


class ComparisonDimension(BaseModel):
    """A dimension comparing two or more papers."""
    name: str = Field(..., description="Comparison dimension (e.g. Time Complexity, Memory, Convergence)")
    paper_a_value: str = Field(..., description="Value/approach in Paper A")
    paper_b_value: str = Field(..., description="Value/approach in Paper B")
    comparative_analysis: str = Field(..., description="Key difference and trade-off")


class ComparisonMatrix(BaseModel):
    """Structured head-to-head comparison between two papers."""
    paper_a_title: str
    paper_b_title: str
    dimensions: List[ComparisonDimension] = Field(default_factory=list)
    trade_off_summary: str = Field(..., description="Summary of fundamental engineering trade-offs")
    recommended_choice: str = Field(..., description="When to choose Paper A vs Paper B")


class OpenReviewReport(BaseModel):
    """Official OpenReview (NeurIPS/ICLR) format peer review."""
    paper_title: str
    summary_of_work: str = Field(..., description="Objective summary of the paper's key claims")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    questions_for_authors: List[str] = Field(default_factory=list)
    soundness_score: int = Field(default=3, ge=1, le=4, description="1=Poor, 2=Fair, 3=Good, 4=Excellent")
    presentation_score: int = Field(default=3, ge=1, le=4, description="1=Poor, 2=Fair, 3=Good, 4=Excellent")
    contribution_score: int = Field(default=3, ge=1, le=4, description="1=Poor, 2=Fair, 3=Good, 4=Excellent")
    overall_recommendation: int = Field(default=6, ge=1, le=10, description="1-10 overall score")
    reproducibility_checklist_passed: bool = Field(default=True)


class DiagramArtifact(BaseModel):
    """Architecture or benchmark diagram artifact."""
    diagram_type: str = Field(..., description="'mermaid' or 'matplotlib'")
    title: str = Field(..., description="Diagram title")
    source_code: str = Field(..., description="Mermaid string or Python matplotlib script")
    artifact_path: Optional[str] = Field(default=None, description="Path to rendered image file if available")


class StoredPaperRecord(BaseModel):
    """Lightweight metadata record for persistent storage."""
    id: str
    title: str
    arxiv_id: Optional[str] = None
    created_at: str
    tags: List[str] = Field(default_factory=list)
    summary: str = ""
    has_code: bool = False


class CitationNode(BaseModel):
    """Node in academic citation lineage graph."""
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    citation_count: Optional[int] = None
    influence_role: str = Field(default="related", description="'foundation', 'baseline', 'successor', 'related'")


class CitationGraph(BaseModel):
    """Citation lineage and related work graph."""
    root_paper_title: str
    nodes: List[CitationNode] = Field(default_factory=list)
    edges: List[Dict[str, str]] = Field(default_factory=list, description="List of {'source': title, 'target': title, 'relation': rel}")
    lineage_summary: str = Field(default="", description="Narrative synthesis of the paper's intellectual lineage")


class TensorDimensionCheck(BaseModel):
    """Tensor dimension and mathematical consistency check."""
    variable_name: str
    expected_shape: str
    math_symbol: str
    is_consistent: bool = True
    explanation: str = ""


class FormulaVerificationReport(BaseModel):
    """Verification of tensor shapes and invariants in mathematical formulations."""
    formula_id: str
    latex: str
    dimensions: List[TensorDimensionCheck] = Field(default_factory=list)
    invariants_passed: bool = True
    dimension_notes: str = ""


class ScalingMeasurement(BaseModel):
    """Empirical scaling benchmark data point."""
    input_scale: int
    latency_ms: float
    memory_peak_mb: float


class ComplexityProfileResult(BaseModel):
    """Algorithmic time/memory scaling analysis."""
    algorithm_name: str
    theoretical_complexity: str = Field(..., description="e.g. O(N^2), O(N log N)")
    empirical_scaling: str = Field(default="", description="Observed empirical scaling behavior")
    measurements: List[ScalingMeasurement] = Field(default_factory=list)
    bottleneck_analysis: str = ""


class FrameworkImplementation(BaseModel):
    """Algorithm implementation in a specific framework."""
    framework: str = Field(..., description="'numpy', 'pytorch', or 'jax'")
    code: str
    entry_function: str
    verified: bool = False


class MultiFrameworkCode(BaseModel):
    """Multi-framework synthesized algorithm suite."""
    paper_title: str
    implementations: Dict[str, FrameworkImplementation] = Field(default_factory=dict)


class CodeMathAlignment(BaseModel):
    """Bidirectional mapping between synthesized code lines and LaTeX equations."""
    function_name: str
    code_line_range: str
    target_formula_id: str
    target_formula_latex: str
    alignment_notes: str = ""


class TraceMap(BaseModel):
    """Complete code-to-paper mathematical tracing map."""
    paper_title: str
    alignments: List[CodeMathAlignment] = Field(default_factory=list)


class SlideDeck(BaseModel):
    """Presentation slide deck generated from paper insights."""
    title: str
    author: str = "PaperAgent AI"
    marp_markdown: str
    slide_count: int

