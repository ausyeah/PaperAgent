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


# ============================================================================
# v0.4.0 Advanced Workstation Schemas
# ============================================================================

class AblationVariant(BaseModel):
    """Ablation component variation."""
    variant_name: str
    modified_component: str
    hypothesis: str
    code_modification: str = ""
    expected_impact: str = ""
    metrics: Dict[str, float] = Field(default_factory=dict)


class AblationStudyResult(BaseModel):
    """Automated ablation study design and benchmark suite."""
    paper_title: str
    baseline_algorithm: str
    variants: List[AblationVariant] = Field(default_factory=list)
    ablation_harness_code: str = ""
    insights_summary: str = ""


class LiteratureSurvey(BaseModel):
    """Systematic survey and related works synthesis."""
    topic: str
    taxonomy_tree: Dict[str, List[str]] = Field(default_factory=dict)
    chronology: List[Dict[str, Any]] = Field(default_factory=list)
    comparative_table: List[Dict[str, Any]] = Field(default_factory=list)
    open_challenges: List[str] = Field(default_factory=list)
    survey_markdown: str = ""


class HardwareProfile(BaseModel):
    """Hardware requirements and hyperparameter optimization profile."""
    model_name: str
    parameter_count_million: float = 0.0
    vram_inference_mb: Dict[str, float] = Field(default_factory=dict)
    vram_training_mb: Dict[str, float] = Field(default_factory=dict)
    recommended_gpu: str = "NVIDIA RTX 4090 / A100"
    optuna_hparam_search_code: str = ""


class ConsensusClaim(BaseModel):
    """Meta-analysis consensus claim across papers."""
    claim: str
    supporting_papers: List[str] = Field(default_factory=list)
    opposing_papers: List[str] = Field(default_factory=list)
    consensus_verdict: str = Field(default="supported", description="'supported', 'contested', 'refuted', 'insufficient_evidence'")
    nuance_analysis: str = ""


class MetaAnalysisReport(BaseModel):
    """Multi-paper cross-validation and consensus meta-analysis."""
    topic: str
    analyzed_papers: List[str] = Field(default_factory=list)
    claims: List[ConsensusClaim] = Field(default_factory=list)
    overall_consensus_summary: str = ""


class EnvironmentBundle(BaseModel):
    """Hermetic reproduction environment and container bundle."""
    paper_title: str
    conda_yaml: str
    dockerfile_cuda: str
    requirements_txt: str
    reproduction_script_sh: str
    reproduction_script_ps1: str


class GroundedCitation(BaseModel):
    """Grounded paper citation in conversational QA."""
    section_title: str
    formula_id: Optional[str] = None
    relevant_quote: str = ""


class QAResponse(BaseModel):
    """Grounded answer from conversational paper assistant."""
    query: str
    answer: str
    citations: List[GroundedCitation] = Field(default_factory=list)
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0)


class PodcastDialogueTurn(BaseModel):
    """Single turn in an academic dialogue script."""
    speaker: str = Field(..., description="e.g. 'Host A (Curious)' or 'Host B (Expert)'")
    speech: str
    tone: str = "conversational"
    timing_seconds: int = 15


class PodcastScript(BaseModel):
    """Engaging academic podcast script (NotebookLM style)."""
    episode_title: str
    hosts: List[str] = Field(default_factory=lambda: ["Alex (Explorer)", "Morgan (Specialist)"])
    turns: List[PodcastDialogueTurn] = Field(default_factory=list)
    total_duration_minutes: float = 0.0
    audio_briefing_markdown: str = ""


class HuggingFaceAdapterResult(BaseModel):
    """HuggingFace PreTrainedModel wrapper synthesis."""
    model_class_name: str
    config_class_name: str
    adapter_module_code: str
    example_usage_code: str


class RebuttalPoint(BaseModel):
    """Point-by-point rebuttal response item."""
    reviewer_id: str
    critique_summary: str
    response_strategy: str
    detailed_rebuttal: str
    proposed_new_experiments: List[str] = Field(default_factory=list)


class RebuttalLetter(BaseModel):
    """Academic conference author rebuttal letter."""
    paper_title: str
    overall_strategy: str
    points: List[RebuttalPoint] = Field(default_factory=list)
    markdown_letter: str = ""


class DailyDigestReport(BaseModel):
    """ArXiv daily radar and watchlist digest report."""
    category_or_query: str
    date: str
    matched_papers: List[Dict[str, Any]] = Field(default_factory=list)
    executive_briefing: str = ""


# ============================================================================
# v0.5.0 Autonomous AI Research Co-Pilot & Kernel Schemas
# ============================================================================

class TritonKernelResult(BaseModel):
    """Synthesized GPU Triton kernel implementation."""
    kernel_name: str
    triton_code: str
    benchmark_harness_code: str
    speedup_vs_eager: str = "2.1x"


class IndividualReview(BaseModel):
    """Review from an individual committee member."""
    reviewer_id: str
    persona: str = Field(..., description="e.g. 'Reviewer 1 (Theory Expert)'")
    score: int = Field(default=6, ge=1, le=10)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    detailed_critique: str = ""


class CommitteeReview(BaseModel):
    """Multi-agent conference review committee with Area Chair meta-review."""
    paper_title: str
    reviews: List[IndividualReview] = Field(default_factory=list)
    meta_review: str = ""
    final_decision: str = Field(default="Accept (Poster)", description="'Accept (Oral)', 'Accept (Poster)', 'Reject'")


class GraphVisualizationBundle(BaseModel):
    """Interactive D3/vis.js citation graph visualization bundle."""
    paper_title: str
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    standalone_html: str = ""


class SyntheticDatasetFixture(BaseModel):
    """Synthetic dataset generator fixture for algorithm verification."""
    dataset_name: str
    generator_code: str
    sample_batch_summary: str = ""
    num_samples: int = 1000


class QuantizationBenchmarkRow(BaseModel):
    """Quantization benchmark row."""
    precision: str = "FP16"
    memory_mb: float = 0.0
    latency_ms: float = 0.0
    relative_perplexity: float = 1.0


class QuantizationProfile(BaseModel):
    """Post-training precision and quantization profile."""
    model_name: str
    precision_rows: List[QuantizationBenchmarkRow] = Field(default_factory=list)
    wrapper_code: str = ""
    recommended_precision: str = "INT8 Weight-Only"


class ReproducibilityScorecard(BaseModel):
    """Official empirical reproducibility evaluation scorecard."""
    paper_title: str
    score: int = Field(default=85, ge=0, le=100)
    criteria_checklist: Dict[str, bool] = Field(default_factory=dict)
    verdict_level: str = "High Reproducibility"
    improvement_recommendations: List[str] = Field(default_factory=list)


class ExtractedTable(BaseModel):
    """Structured table extracted from paper text/LaTeX."""
    table_id: str
    caption: str = ""
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    csv_data: str = ""


class ExtractedTableCollection(BaseModel):
    """Collection of extracted paper tables."""
    paper_title: str
    tables: List[ExtractedTable] = Field(default_factory=list)


class SyncBotBundle(BaseModel):
    """Automated Git pull request and Overleaf sync bundle."""
    target_repo: str
    pr_title: str
    pr_body: str
    git_commands: List[str] = Field(default_factory=list)


class DerivationStep(BaseModel):
    """Intermediate step in mathematical derivation."""
    step_number: int
    latex_expression: str
    justification: str


class DerivationVerificationResult(BaseModel):
    """Symbolic verification of formula derivation."""
    formula_from_id: str
    formula_to_id: str
    steps: List[DerivationStep] = Field(default_factory=list)
    is_mathematically_sound: bool = True
    algebraic_notes: str = ""


class SSMLPodcastBundle(BaseModel):
    """Phonetic SSML audio podcast speech bundle."""
    episode_title: str
    ssml_content: str
    tts_script_py: str
    phonetic_glossary: Dict[str, str] = Field(default_factory=dict)


class TopicCluster(BaseModel):
    """Semantic topic cluster in paper library."""
    cluster_name: str
    keywords: List[str] = Field(default_factory=list)
    paper_ids: List[str] = Field(default_factory=list)
    summary: str = ""


class TopicClusterCollection(BaseModel):
    """Collection of semantic topic clusters."""
    clusters: List[TopicCluster] = Field(default_factory=list)


class InteractiveNotebookBundle(BaseModel):
    """Interactive Jupyter notebook with sliders and widgets."""
    notebook_json: str
    widget_features: List[str] = Field(default_factory=list)
    file_path: Optional[str] = None


class BenchmarkEvaluationResult(BaseModel):
    """End-to-end reproduction benchmark evaluation result."""
    paper_name: str
    reproduction_success: bool = True
    execution_time_seconds: float = 0.0
    throughput_samples_per_sec: float = 0.0
    convergence_metric: Dict[str, float] = Field(default_factory=dict)
    summary: str = ""


class SpeedupComparisonResult(BaseModel):
    """Cross-runtime speedup comparison result (PyTorch vs JAX vs Triton)."""
    algorithm_name: str
    framework_latencies_ms: Dict[str, float] = Field(default_factory=dict)
    speedup_ratios: Dict[str, float] = Field(default_factory=dict)
    fastest_framework: str = "triton"
    efficiency_notes: str = ""


# ============================================================================
# v0.6.0 Autonomous AI Scientist & Self-Evolving Algorithm Lab Schemas
# ============================================================================

class ResearchHypothesis(BaseModel):
    """Autonomous algorithmic mutation and research hypothesis."""
    hypothesis_id: str
    title: str
    rationale: str
    proposed_modification: str
    expected_gain: str
    feasibility_score: float = Field(default=0.8, ge=0.0, le=1.0)
    validation_protocol: str = ""


class HypothesisCollection(BaseModel):
    """Collection of generated scientific research hypotheses."""
    paper_title: str
    hypotheses: List[ResearchHypothesis] = Field(default_factory=list)
    strategic_summary: str = ""


class SelfHealingPatch(BaseModel):
    """Single diagnostic fix step in autonomous code healing."""
    iteration: int
    error_type: str
    error_message: str
    diagnosis: str
    patch_applied: str


class SelfHealingResult(BaseModel):
    """Result of multi-iteration autonomous execution self-healing."""
    success: bool
    iterations_run: int
    patches: List[SelfHealingPatch] = Field(default_factory=list)
    final_code: str
    final_stdout: str = ""
    final_stderr: str = ""


class GradientCheckItem(BaseModel):
    """Individual numerical vs analytical gradient verification entry."""
    parameter_name: str
    analytical_grad_norm: float
    numerical_grad_norm: float
    relative_difference: float
    is_differentiable: bool = True


class GradientVerificationReport(BaseModel):
    """Autograd differentiation and numerical gradient verification report."""
    module_name: str
    checks: List[GradientCheckItem] = Field(default_factory=list)
    all_passed: bool = True
    gradient_health: str = "Healthy"
    summary_notes: str = ""


class MemoryAllocationEvent(BaseModel):
    """Tensor memory allocation event in execution trace."""
    operation_name: str
    allocated_mb: float
    peak_mb: float
    notes: str = ""


class MemoryTraceProfile(BaseModel):
    """CUDA/CPU peak memory profile and allocation snapshot."""
    module_name: str
    peak_memory_mb: float
    activation_memory_mb: float
    parameter_memory_mb: float
    events: List[MemoryAllocationEvent] = Field(default_factory=list)
    memory_efficiency_verdict: str = "Optimal"
    optimization_recommendations: List[str] = Field(default_factory=list)


class CandidateArchitecture(BaseModel):
    """Candidate architecture evaluated during evolutionary search."""
    candidate_id: str
    topology_summary: str
    parameter_count_m: float
    simulated_accuracy: float
    latency_ms: float
    pareto_optimal: bool = False


class EvolutionarySearchResult(BaseModel):
    """Evolutionary neural architecture and operator search result."""
    base_algorithm: str
    generations_evaluated: int
    candidates: List[CandidateArchitecture] = Field(default_factory=list)
    best_candidate_id: str
    evolutionary_insights: str = ""


class FigureNode(BaseModel):
    """Node in parsed academic diagram DAG."""
    node_id: str
    label: str
    node_type: str = "operator"


class FigureEdge(BaseModel):
    """Directed connection in diagram DAG."""
    source_id: str
    target_id: str
    tensor_flow_desc: str = ""


class FigureSemanticGraph(BaseModel):
    """Semantic graph deconstructed from an academic paper figure."""
    figure_id: str
    caption: str = ""
    nodes: List[FigureNode] = Field(default_factory=list)
    edges: List[FigureEdge] = Field(default_factory=list)
    synthesized_code_stub: str = ""


class CanonicalMathExpression(BaseModel):
    """Canonicalized mathematical expression converted into SymPy."""
    original_latex: str
    canonical_sympy: str
    symbols: List[str] = Field(default_factory=list)
    is_solvable: bool = True


class MathNormalizationCollection(BaseModel):
    """Collection of normalized mathematical expressions."""
    paper_title: str
    expressions: List[CanonicalMathExpression] = Field(default_factory=list)


class HybridSynthesisResult(BaseModel):
    """Synthesized hybrid algorithm fusing innovations from multiple papers."""
    source_paper_a: str
    source_paper_b: str
    hybrid_algorithm_name: str
    fusion_rationale: str
    hybrid_code: str
    test_suite_code: str


class BenchmarkMetricRecord(BaseModel):
    """Record on academic benchmark leaderboard."""
    benchmark_name: str
    sota_score: float
    paper_score: float
    relative_gap_pct: float
    is_new_sota: bool = False


class LeaderboardSnapshot(BaseModel):
    """Historical and current benchmark leaderboard trajectory."""
    paper_title: str
    metrics: List[BenchmarkMetricRecord] = Field(default_factory=list)
    saturation_verdict: str = "Active Competition"


class PosterSection(BaseModel):
    """Section content for academic conference poster."""
    title: str
    content_html: str
    order: int


class AcademicPosterBundle(BaseModel):
    """Responsive high-resolution academic conference poster bundle."""
    paper_title: str
    authors: List[str] = Field(default_factory=list)
    sections: List[PosterSection] = Field(default_factory=list)
    standalone_poster_html: str = ""


class ONNXExportBundle(BaseModel):
    """ONNX and TensorRT compilation script bundle."""
    model_name: str
    onnx_export_script_py: str
    tensorrt_builder_script_py: str
    opset_version: int = 17
    simplification_instructions: str = ""


class DistributedLaunchBundle(BaseModel):
    """Multi-GPU PyTorch DDP / FSDP distributed launcher bundle."""
    model_name: str
    ddp_launcher_script_py: str
    fsdp_config_yaml: str
    slurm_batch_script_sh: str
    recommended_world_size: int = 8


class SemanticDiffItem(BaseModel):
    """Itemized difference between paper revisions."""
    section_title: str
    change_type: str = "modified"  # 'added', 'removed', 'modified'
    v1_summary: str = ""
    v2_summary: str = ""
    significance: str = "Medium"


class PaperSemanticDiff(BaseModel):
    """Semantic evolution diff between paper versions (e.g. v1 vs v2)."""
    paper_title: str
    v1_identifier: str = "v1"
    v2_identifier: str = "v2"
    diff_items: List[SemanticDiffItem] = Field(default_factory=list)
    executive_diff_summary: str = ""


class ExperimentRunRecord(BaseModel):
    """Single run in an autonomous experiment matrix."""
    run_id: str
    seed: int
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    final_metric: float
    duration_seconds: float
    status: str = "COMPLETED"


class ExperimentMatrixResult(BaseModel):
    """Result of grid/random autonomous experiment sweep."""
    matrix_name: str
    total_runs: int
    runs: List[ExperimentRunRecord] = Field(default_factory=list)
    best_run_id: str
    aggregate_statistics: Dict[str, float] = Field(default_factory=dict)
    ascii_summary: str = ""





