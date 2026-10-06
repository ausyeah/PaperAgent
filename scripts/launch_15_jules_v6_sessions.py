"""
Orchestrates launching 15 parallel Jules sessions for PaperAgent v0.6.0:
Autonomous AI Scientist & Self-Evolving Algorithm Lab
"""

import os
import sys
import json
import time
import requests

JULES_API_KEY = os.environ.get("JULES_API_KEY")
if not JULES_API_KEY:
    print("Error: JULES_API_KEY not set")
    sys.exit(1)

HEADERS = {
    "x-goog-api-key": JULES_API_KEY,
    "Content-Type": "application/json"
}

SOURCE_NAME = "sources/github/ausyeah/PaperAgent"

TASKS = [
    {
        "id": "task_1_hypothesis_generator",
        "title": "feat(engine): implement automated scientific hypothesis generator",
        "prompt": """Task: Implement Automated Scientific Hypothesis Generator in `paperagent/engine/hypothesis.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `ResearchHypothesis` and `HypothesisCollection` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/hypothesis.py`
   - Class `ScientificHypothesisGenerator`:
     * `generate_hypotheses(self, paper: ParsedPaper, client: Optional[LLMClient] = None) -> HypothesisCollection`:
       Analyzes paper limitations, mathematical formulations, and empirical baselines.
       Generates 3-5 concrete algorithmic mutations/hypotheses (`ResearchHypothesis`) with rationales, expected gains, feasibility scores (0.0 to 1.0), and validation protocols.
       Deterministic offline heuristic fallback when LLM is unavailable.
2. File: `tests/test_hypothesis.py`
   - Unit tests verifying hypothesis generation, model fields, feasibility bounds, and offline fallback.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_2_self_debugger",
        "title": "feat(runner): implement autonomous execution-feedback self-healing loop",
        "prompt": """Task: Implement Autonomous Execution-Feedback Self-Healing Loop in `paperagent/runner/self_debugger.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `SelfHealingResult` and `SelfHealingPatch` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/runner/self_debugger.py`
   - Class `SelfHealingDebugger`:
     * `heal_code(self, code: str, max_iterations: int = 3, client: Optional[LLMClient] = None) -> SelfHealingResult`:
       Executes code in a sandbox (`ExecutionSandbox` from `paperagent.runner`).
       If execution fails (e.g., SyntaxError, NameError, ZeroDivisionError, shape mismatch), diagnoses root cause and applies automated patch.
       Repeats up to `max_iterations` until code executes cleanly or max iterations reached.
       Provides deterministic regex/rule-based offline fix heuristics (e.g., auto-importing missing math/numpy, fixing undefined vars).
2. File: `tests/test_self_debugger.py`
   - Unit tests verifying code healing on buggy code samples (syntax error, missing import, runtime error) and return model fields.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_3_gradient_verifier",
        "title": "feat(engine): implement numerical gradient and autograd invariant verifier",
        "prompt": """Task: Implement Numerical Gradient & Autograd Invariant Verifier in `paperagent/engine/gradient_verifier.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `GradientVerificationReport` and `GradientCheckItem` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/gradient_verifier.py`
   - Class `GradientVerifier`:
     * `verify_gradients(self, func_or_code: str, input_dim: int = 4, epsilon: float = 1e-5) -> GradientVerificationReport`:
       Performs finite-difference gradient checking against analytical gradients:
       $g_{num} = \\frac{f(x+\\epsilon) - f(x-\\epsilon)}{2\\epsilon}$.
       Computes relative difference $|g_{num} - g_{ana}| / (|g_{num}| + |g_{ana}| + 1e-8)$.
       Checks if gradient is mathematically sound, finite (no NaN/Inf), and non-zero.
       Pure Python / NumPy deterministic fallback when PyTorch is not available.
2. File: `tests/test_gradient_verifier.py`
   - Unit tests verifying differentiable functions (e.g., sigmoid, quadratic, linear) and detection of gradient anomalies.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_4_memory_tracer",
        "title": "feat(synthesizer): implement granular peak memory profiler and allocation snapshot generator",
        "prompt": """Task: Implement Granular Peak Memory Profiler in `paperagent/synthesizer/memory_tracer.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `MemoryTraceProfile` and `MemoryAllocationEvent` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/memory_tracer.py`
   - Class `MemoryTracer`:
     * `profile_memory(self, project: PaperProject) -> MemoryTraceProfile`:
       Models tensor memory allocation per operator/layer based on paper parameters and batch shapes.
       Calculates peak memory MB, activation memory MB, parameter memory MB.
       Generates itemized `MemoryAllocationEvent` items and memory efficiency verdicts ('Optimal', 'Moderate', 'High VRAM Overhead').
       Outputs concrete actionable optimization recommendations (e.g. gradient checkpointing, flash attention, FP16 mixed precision).
2. File: `tests/test_memory_tracer.py`
   - Unit tests verifying memory calculations, event tracking, and recommendations.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_5_evolutionary_search",
        "title": "feat(engine): implement evolutionary neural architecture search engine",
        "prompt": """Task: Implement Evolutionary Neural Architecture Search Engine in `paperagent/engine/evolutionary_search.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `EvolutionarySearchResult` and `CandidateArchitecture` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/evolutionary_search.py`
   - Class `EvolutionaryArchitectureSearch`:
     * `search(self, base_algorithm: str, generations: int = 5, population_size: int = 6) -> EvolutionarySearchResult`:
       Evolves architecture topology variations (e.g. layer depth, attention heads, expansion ratios, activation functions).
       Evaluates candidate fitness based on simulated accuracy vs latency/parameter trade-offs.
       Identifies Pareto-optimal candidates and best candidate ID.
       Deterministic offline search execution with reproducible seed.
2. File: `tests/test_evolutionary_search.py`
   - Unit tests verifying generation cycles, candidate population mutation, Pareto frontier marking, and result model.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_6_figure_describer",
        "title": "feat(parser): implement academic architecture diagram and figure deconstructor",
        "prompt": """Task: Implement Academic Architecture Diagram Deconstructor in `paperagent/parser/figure_describer.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `FigureSemanticGraph`, `FigureNode`, and `FigureEdge` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/parser/figure_describer.py`
   - Class `FigureDeconstructor`:
     * `deconstruct_figure(self, figure_caption: str, context_text: str = "") -> FigureSemanticGraph`:
       Parses architectural descriptions and figure captions (e.g. "Figure 1: Overview of our Dual-Path Transformer").
       Extracts operator nodes (`FigureNode`), directed dataflow edges (`FigureEdge`), and synthesizes an executable code stub skeleton matching the graph.
       Deterministic regex/heuristic fallback for offline execution.
2. File: `tests/test_figure_describer.py`
   - Unit tests verifying DAG node/edge extraction from sample figure captions and code stub generation.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_7_latex_math_normalizer",
        "title": "feat(parser): implement LaTeX math canonicalizer and SymPy normalizer",
        "prompt": """Task: Implement LaTeX Math Canonicalizer in `paperagent/parser/math_normalizer.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `CanonicalMathExpression` and `MathNormalizationCollection` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/parser/math_normalizer.py`
   - Class `MathNormalizer`:
     * `normalize_latex(self, latex_str: str) -> CanonicalMathExpression`:
       Cleans and canonicalizes raw LaTeX equations (strips `\\left`, `\\right`, whitespace quirks, normalizes fractions `\\frac{a}{b}` -> `a/b`, converts superscripts/subscripts).
       Extracts unique math symbol tokens.
       Generates normalized SymPy-compatible expression string.
     * `normalize_paper_formulas(self, paper: ParsedPaper) -> MathNormalizationCollection`:
       Processes all extracted formulas in a paper.
2. File: `tests/test_math_normalizer.py`
   - Unit tests testing normalization of fractions, powers, Greek letters, and symbol extraction.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_8_multi_paper_synthesizer",
        "title": "feat(engine): implement cross-paper algorithm fusion and hybrid synthesizer",
        "prompt": """Task: Implement Cross-Paper Algorithm Fusion in `paperagent/engine/multi_paper_synthesizer.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `HybridSynthesisResult` is already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/multi_paper_synthesizer.py`
   - Class `CrossPaperFusionSynthesizer`:
     * `fuse_papers(self, paper_a: ParsedPaper, paper_b: ParsedPaper, client: Optional[LLMClient] = None) -> HybridSynthesisResult`:
       Identifies complementary strengths of Paper A and Paper B (e.g., Mamba state space + Transformer multi-head attention).
       Synthesizes a unified hybrid algorithm (`HybridSynthesisResult`) with clear fusion rationale, target Python code, and test suite code.
       Robust offline template fallback when LLM is unavailable.
2. File: `tests/test_multi_paper_synthesizer.py`
   - Unit tests verifying paper fusion, generated hybrid code syntax, and test suite validity.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_9_leaderboard_tracker",
        "title": "feat(storage): implement benchmark leaderboard and SOTA saturation tracker",
        "prompt": """Task: Implement Benchmark Leaderboard Tracker in `paperagent/storage/leaderboard.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `LeaderboardSnapshot` and `BenchmarkMetricRecord` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/storage/leaderboard.py`
   - Class `LeaderboardTracker`:
     * `track_paper_performance(self, paper: ParsedPaper, custom_benchmarks: Optional[Dict[str, float]] = None) -> LeaderboardSnapshot`:
       Parses empirical benchmark claims from paper text/tables against historical SOTA records (e.g. ImageNet Top-1, GLUE, MMLU, GSM8K).
       Calculates relative gap percentage and flags `is_new_sota`.
       Computes `saturation_verdict` ('Approaching Ceiling', 'Active Competition', 'Early Breakthrough').
2. File: `tests/test_leaderboard.py`
   - Unit tests verifying metric matching, gap calculation, SOTA flagging, and saturation detection.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_10_conference_poster",
        "title": "feat(export): implement automated academic conference poster generator",
        "prompt": """Task: Implement Academic Conference Poster Generator in `paperagent/export/poster.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `AcademicPosterBundle` and `PosterSection` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/poster.py`
   - Class `AcademicPosterGenerator`:
     * `generate_poster(self, project: PaperProject, output_path: Optional[str] = None) -> AcademicPosterBundle`:
       Synthesizes a 3-column academic conference poster HTML/CSS bundle:
       Column 1: Motivation, Problem Formulation, Background.
       Column 2: Proposed Architecture, Core Equations, Key Innovation.
       Column 3: Experimental Results, Table Comparison, Conclusion.
       Responsive, publication-grade CSS with KaTeX formulas and clean color scheme.
       Saves to `output_path` if specified.
2. File: `tests/test_poster.py`
   - Unit tests verifying poster generation, HTML structure, section ordering, and file export.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_11_onnx_tensorrt_exporter",
        "title": "feat(export): implement ONNX and TensorRT compilation script bundle generator",
        "prompt": """Task: Implement ONNX & TensorRT Compilation Generator in `paperagent/export/onnx_exporter.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `ONNXExportBundle` is already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/onnx_exporter.py`
   - Class `ONNXExportGenerator`:
     * `generate_export_bundle(self, project: PaperProject, opset_version: int = 17) -> ONNXExportBundle`:
       Synthesizes `onnx_export_script_py` using `torch.onnx.export` with dynamic axes (batch_size, sequence_length).
       Synthesizes `tensorrt_builder_script_py` using TensorRT Python API (`tensorrt.Builder`, `NetworkDefinition`, `BuilderConfig`, FP16/INT8 flags).
       Provides simplification instructions using `onnxsim`.
2. File: `tests/test_onnx_exporter.py`
   - Unit tests verifying Python script syntax via `ast.parse` and return model fields.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_12_distributed_ddp",
        "title": "feat(synthesizer): implement multi-GPU PyTorch DDP and FSDP distributed launcher bundle",
        "prompt": """Task: Implement Distributed Launcher Generator in `paperagent/synthesizer/distributed_launcher.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `DistributedLaunchBundle` is already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/distributed_launcher.py`
   - Class `DistributedLaunchGenerator`:
     * `generate_distributed_bundle(self, project: PaperProject, world_size: int = 8) -> DistributedLaunchBundle`:
       Synthesizes `ddp_launcher_script_py` using `torch.distributed.run` / `mp.spawn` with `DistributedSampler` and `DistributedDataParallel`.
       Synthesizes `fsdp_config_yaml` for Fully Sharded Data Parallelism with auto-wrap policies.
       Synthesizes `slurm_batch_script_sh` for HPC cluster job submission.
2. File: `tests/test_distributed_launcher.py`
   - Unit tests verifying Python AST validity, YAML validity, and Slurm script generation.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_13_semantic_diff",
        "title": "feat(engine): implement versioned paper semantic diff and evolution engine",
        "prompt": """Task: Implement Paper Semantic Diff Engine in `paperagent/engine/semantic_diff.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `PaperSemanticDiff` and `SemanticDiffItem` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/semantic_diff.py`
   - Class `PaperSemanticDiffEngine`:
     * `diff_papers(self, paper_v1: ParsedPaper, paper_v2: ParsedPaper, client: Optional[LLMClient] = None) -> PaperSemanticDiff`:
       Compares two versions of a paper (e.g. ArXiv v1 vs v2).
       Identifies added, removed, and modified sections, changes in experimental metrics, and revised claims.
       Computes itemized `SemanticDiffItem` records and an `executive_diff_summary`.
       Deterministic offline text-matching fallback.
2. File: `tests/test_semantic_diff.py`
   - Unit tests verifying diff detection between synthetic paper revisions.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_14_synthetic_experiment_runner",
        "title": "feat(runner): implement autonomous experiment matrix grid sweep runner",
        "prompt": """Task: Implement Autonomous Experiment Matrix Runner in `paperagent/runner/experiment_runner.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `ExperimentMatrixResult` and `ExperimentRunRecord` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/runner/experiment_runner.py`
   - Class `ExperimentMatrixRunner`:
     * `run_matrix(self, matrix_name: str, hparam_grid: Dict[str, List[Any]], seeds: List[int] = [42, 123]) -> ExperimentMatrixResult`:
       Executes combinations of hyperparameters across multiple seeds deterministically.
       Records `ExperimentRunRecord` for each run with simulated duration, metrics, and hyperparameters.
       Computes aggregate statistics (mean, std, min, max) and formats a clean ASCII summary table.
2. File: `tests/test_experiment_runner.py`
   - Unit tests verifying grid expansion, execution records, aggregation statistics, and ASCII summary.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_15_web_ui_v6",
        "title": "feat(web): expand single-page dashboard with autonomous AI scientist views",
        "prompt": """Task: Expand Web UI Dashboard in `paperagent/web/static/app.js` and `paperagent/web/static/index.html`

Context:
See `paperagent/web/static/index.html` and `paperagent/web/static/app.js`.

Requirements:
1. File: `paperagent/web/static/index.html`
   - Add tab headers and container panels for:
     - 'AI Scientist Hypotheses' (`tab-hypotheses`)
     - 'Self-Healing Debugger' (`tab-debugger`)
     - 'Conference Poster' (`tab-poster`)
2. File: `paperagent/web/static/app.js`
   - Add render functions:
     - `renderHypotheses(hypothesesData)`
     - `renderSelfHealing(healingData)`
     - `renderPoster(posterData)`
3. File: `tests/test_v6_ui.py`
   - Unit tests verifying HTML structure, new container IDs (`tab-hypotheses`, `tab-debugger`, `tab-poster`), and JS functions in app.js.

Ensure clean code, type annotations, and robust error handling."""
    }
]

def main():
    print(f"Launching 15 concurrent Jules sessions for Sprint v0.6.0...")
    os.makedirs(".jules", exist_ok=True)
    active_path = ".jules/active_sessions_v6.json"
    
    active_sessions = []
    
    for task in TASKS:
        url = "https://jules.googleapis.com/v1alpha/sessions"
        body = {
            "sourceContext": {
                "source": SOURCE_NAME,
                "githubRepoContext": {
                    "startingBranch": "main"
                }
            },
            "prompt": f"Title: {task['title']}\n\n{task['prompt']}"
        }
        print(f"Launching {task['id']}...")
        try:
            res = requests.post(url, headers=HEADERS, json=body, timeout=30)
            if res.status_code in (200, 201):
                data = res.json()
                session_id = data.get("name", "").split("/")[-1]
                print(f"  -> SUCCESS: Session ID: {session_id}")
                active_sessions.append({
                    "task_id": task["id"],
                    "title": task["title"],
                    "session": data.get("name"),
                    "session_name": data.get("name"),
                    "session_id": session_id,
                    "created_at": time.time()
                })
            else:
                print(f"  -> FAILED: HTTP {res.status_code}: {res.text}")
        except Exception as e:
            print(f"  -> EXCEPTION: {e}")
        time.sleep(1)
        
    with open(active_path, "w", encoding="utf-8") as f:
        json.dump(active_sessions, f, indent=2)
        
    print(f"\nTotal active v6 sessions dispatched: {len(active_sessions)} / 15 saved in {active_path}")

if __name__ == "__main__":
    main()
