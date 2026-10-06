"""
Script to launch 10 concurrent Jules coding sessions for PaperAgent v0.3.0.
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
        "id": "task_1_citation_graph",
        "title": "feat(parser): implement academic citation lineage and related work graph builder",
        "prompt": """Task: Implement Citation Lineage Graph in `paperagent/parser/citation_graph.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `CitationNode` and `CitationGraph` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/parser/citation_graph.py`
   - Class `CitationGraphBuilder`:
     * `__init__(self, llm_client: Optional[LLMClient] = None)`
     * `build_citation_graph(self, paper: ParsedPaper) -> CitationGraph`:
       Analyzes bibliography references in paper text and sections.
       Extracts reference entries (title, authors, year, arxiv_id, doi).
       Classifies each reference's intellectual role:
         - 'foundation': Theoretical baseline or core theorem the paper builds directly upon.
         - 'baseline': Benchmark model compared against in experiments.
         - 'successor': Follow-up or inspired works.
         - 'related': Background work in the same domain.
       Builds nodes (List[CitationNode]) and directed edges (List[Dict[str, str]]).
       Generates `lineage_summary` describing how the paper evolves from prior art.
     * Offline / Mock mode fallback with pre-baked valid citation graph if LLM is offline or in mock mode.
2. File: `tests/test_citation_graph.py`
   - Unit tests verifying nodes, edges, role classification, and lineage summary generation.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_2_formula_checker",
        "title": "feat(engine): implement tensor dimension invariant and mathematical consistency verifier",
        "prompt": """Task: Implement Formula Dimension & Invariant Verifier in `paperagent/engine/formula_checker.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `TensorDimensionCheck` and `FormulaVerificationReport` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/formula_checker.py`
   - Class `FormulaDimensionChecker`:
     * `__init__(self, llm_client: Optional[LLMClient] = None)`
     * `verify_formula(self, formula: ExtractedFormula, paper: Optional[ParsedPaper] = None) -> FormulaVerificationReport`:
       Performs symbolic dimension analysis on the LaTeX equation (e.g. matrix multiplications, attention projections, layer norm).
       Checks each mathematical symbol (variable_name, expected_shape, math_symbol, is_consistent, explanation).
       Validates whether tensor dimension invariants hold (e.g. batch size B, sequence length S, hidden dimension D).
       Produces `FormulaVerificationReport(formula_id=..., latex=..., dimensions=..., invariants_passed=..., dimension_notes=...)`.
     * Offline / Mock mode fallback with realistic verification results.
2. File: `tests/test_formula_checker.py`
   - Unit tests with mock formulas (e.g. Attention equation $Q K^T / \\sqrt{d_k}$) verifying dimension checks and report generation.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_3_profiler",
        "title": "feat(synthesizer): implement algorithmic scaling complexity and memory profiler",
        "prompt": """Task: Implement Algorithmic Complexity & Scaling Profiler in `paperagent/synthesizer/profiler.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `ScalingMeasurement` and `ComplexityProfileResult` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/profiler.py`
   - Class `ComplexityProfiler`:
     * `profile_code(self, code: str, scales: List[int] = [32, 64, 128], timeout_per_scale: float = 5.0) -> ComplexityProfileResult`:
       Safely profiles execution of code across given input scales using subprocess or execution harness.
       Uses `tracemalloc` for peak memory (MB) and `time.perf_counter` for latency (ms).
       Analyzes growth rate to classify `empirical_scaling` (e.g. 'O(N) Linear', 'O(N^2) Quadratic', 'O(N log N)').
       Detects memory or compute bottlenecks and fills `bottleneck_analysis`.
       Produces `ComplexityProfileResult(algorithm_name=..., theoretical_complexity=..., empirical_scaling=..., measurements=..., bottleneck_analysis=...)`.
     * Mock / fallback mode when code execution fails or runs in restricted environments.
2. File: `tests/test_profiler.py`
   - Unit tests profiling trivial linear (sum) and quadratic (nested loop) functions, verifying measurements and scaling classification.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_4_transpiler",
        "title": "feat(synthesizer): implement multi-framework transpiler for NumPy, PyTorch, and JAX",
        "prompt": """Task: Implement Multi-Framework Transpiler in `paperagent/synthesizer/transpiler.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `FrameworkImplementation` and `MultiFrameworkCode` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/transpiler.py`
   - Class `MultiFrameworkTranspiler`:
     * `__init__(self, llm_client: Optional[LLMClient] = None)`
     * `transpile_all(self, paper: ParsedPaper, base_code: Optional[str] = None) -> MultiFrameworkCode`:
       Produces implementations in three target frameworks:
         - 'numpy': Pure NumPy vectorized implementation.
         - 'pytorch': PyTorch `torch.nn.Module` class with forward() method and type annotations.
         - 'jax': JAX / Flax functional implementation with `@jax.jit` compatibility.
       Validates generated Python syntax using `ast.parse` for each framework implementation.
       Produces `MultiFrameworkCode(paper_title=..., implementations={...})`.
     * Offline / Mock mode fallback with pre-baked valid syntax implementations for the 3 frameworks.
2. File: `tests/test_transpiler.py`
   - Unit tests verifying all 3 frameworks are present and pass `ast.parse` without SyntaxError.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_5_code_aligner",
        "title": "feat(engine): implement bidirectional code-to-paper mathematical trace aligner",
        "prompt": """Task: Implement Code-to-Paper Trace Aligner in `paperagent/engine/code_aligner.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `CodeMathAlignment` and `TraceMap` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/code_aligner.py`
   - Class `CodeMathAligner`:
     * `__init__(self, llm_client: Optional[LLMClient] = None)`
     * `align_code_with_paper(self, paper: ParsedPaper, synthesis: SynthesisResult) -> TraceMap`:
       Analyzes synthesized Python code against the paper's formulas and sections.
       Maps specific functions or line blocks to the corresponding mathematical formulas.
       For each alignment:
         - `function_name`: name of function or block
         - `code_line_range`: e.g. "L12-L28"
         - `target_formula_id`: e.g. "formula-1"
         - `target_formula_latex`: LaTeX equation string
         - `alignment_notes`: explanation of how code variables correspond to math symbols.
       Produces `TraceMap(paper_title=..., alignments=...)`.
     * Offline / Mock mode fallback with realistic alignment mappings.
2. File: `tests/test_code_aligner.py`
   - Unit tests verifying `TraceMap` generation, alignment fields, and formula matching.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_6_vector_index",
        "title": "feat(storage): implement BM25 and TF-IDF semantic search index for paper library",
        "prompt": """Task: Implement BM25 & TF-IDF Search Index in `paperagent/storage/vector_index.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `StoredPaperRecord` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/storage/vector_index.py`
   - Class `PaperSearchIndex`:
     * Pure-Python, zero-heavy-dependency search index using TF-IDF / BM25 algorithms.
     * Tokenizes title, summary, and tags (lowercasing, stopword filtering, word frequency).
     * `add_paper(self, record: StoredPaperRecord) -> None`: indexes a paper record.
     * `remove_paper(self, paper_id: str) -> bool`: removes from index.
     * `search(self, query: str, top_k: int = 10) -> List[Tuple[StoredPaperRecord, float]]`:
       Scores papers against query terms using BM25 scoring and returns ranked records with relevance scores.
     * `size(self) -> int`: number of indexed papers.
2. File: `tests/test_vector_index.py`
   - Unit tests testing index building, BM25 ranking, searching for multi-word queries, and record deletion.

Ensure clean code, type annotations, and fast execution."""
    },
    {
        "id": "task_7_slides_export",
        "title": "feat(export): implement Marp and Reveal presentation slide deck generator",
        "prompt": """Task: Implement Marp Slide Deck Generator in `paperagent/export/slides.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `SlideDeck` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/slides.py`
   - `generate_marp_slides(project: PaperProject) -> SlideDeck`:
     Generates clean, presentation-ready Marp markdown:
     * Marp frontmatter: `marp: true`, `theme: gaia`, `paginate: true`, `math: katex`.
     * Slide 1: Title slide with paper title, authors, and PaperAgent badge.
     * Slide 2: Motivation & Executive Brief.
     * Slide 3: Core Mathematical Formulation (clean KaTeX blocks).
     * Slide 4: Algorithmic Innovation & Pseudocode.
     * Slide 5: Python Reproduction Implementation (`python` code fence).
     * Slide 6: NeurIPS Reviewer Critique (strengths, weaknesses, score badge).
     * Slide 7: Conclusion & Key Takeaways.
     * Counts slides (delimited by `---`) and produces `SlideDeck(title=..., author=..., marp_markdown=..., slide_count=...)`.
   - `export_slides_file(project: PaperProject, output_path: str) -> str`:
     Writes markdown to file and returns path.
2. File: `tests/test_slides_export.py`
   - Unit tests verifying Marp frontmatter, slide delimiter count, KaTeX math blocks, and file export.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_8_ci_action",
        "title": "feat(export): implement GitHub Actions paper reproduction workflow generator",
        "prompt": """Task: Implement GitHub Actions Reproduction Exporter in `paperagent/export/ci_action.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/ci_action.py`
   - `generate_github_workflow(project: PaperProject) -> str`:
     Generates valid YAML string for `.github/workflows/reproduce.yml`:
     * Workflow triggers on `push` and `workflow_dispatch`.
     * Jobs: `matrix` for Python versions (3.10, 3.11).
     * Steps: checkout, setup-python, install dependencies, run pytest suite, run benchmark script.
   - `export_reproduction_repo_bundle(project: PaperProject, output_zip_path: str) -> str`:
     Packages a standalone reproduction git repo archive as `.zip`:
     * `.github/workflows/reproduce.yml`
     * `reproduce.py`: core synthesized implementation
     * `test_reproduce.py`: pytest test suite
     * `requirements.txt`: minimal dependencies
     * `README.md`: one-command setup and reproduction instructions.
     Returns the path to output zip.
2. File: `tests/test_ci_action.py`
   - Unit tests verifying YAML syntax contains required steps and export bundle zip contains expected files.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_9_tui",
        "title": "feat(tui): implement Rich-based full-screen interactive terminal dashboard",
        "prompt": """Task: Implement Terminal UI (TUI) Dashboard in `paperagent/tui.py`

Context:
See `paperagent/cli.py` and `paperagent/models.py`.

Requirements:
1. File: `paperagent/tui.py`
   - Uses `rich` (already in requirements.txt) panels, tables, layouts, and syntax highlighters.
   - Functions:
     * `render_header() -> Panel`: renders styled PaperAgent ASCII banner and version.
     * `render_paper_summary(paper: ParsedPaper) -> Panel`: metadata table with authors, arxiv id, abstract, section outline.
     * `render_analysis_view(analysis: AnalysisReport) -> Panel`: executive summary, problem statement, key insights.
     * `render_formula_gallery(formulas: List[ExtractedFormula]) -> Table`: table of equations and LaTeX representations.
     * `render_code_view(synthesis: SynthesisResult) -> Panel`: Python code with syntax highlighting.
     * `render_openreview_card(review: OpenReviewReport) -> Panel`: formatted review card with score badges (1-10) and checklist.
     * `run_interactive_viewer(project: PaperProject) -> None`: console viewer allowing user to inspect sections.
2. File: `tests/test_tui.py`
   - Unit tests calling the rendering functions with synthetic objects and verifying returned `Panel` / `Table` objects without errors.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_10_api_v3",
        "title": "feat(web): implement v0.3.0 REST routes for citation graph, slides, and profiling",
        "prompt": """Task: Implement v0.3.0 REST Routes in `paperagent/web/v3_routes.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.

Requirements:
1. File: `paperagent/web/v3_routes.py`
   - FastAPI `router = APIRouter(prefix="/api/v3", tags=["v3"])`
   - Endpoints:
     * `POST /api/v3/citation-graph`: accepts `ParsedPaper`, returns `CitationGraph`.
     * `POST /api/v3/formula/verify`: accepts `ExtractedFormula`, returns `FormulaVerificationReport`.
     * `POST /api/v3/code/transpile`: accepts `ParsedPaper`, returns `MultiFrameworkCode`.
     * `POST /api/v3/code/align`: accepts `{"paper": ParsedPaper, "synthesis": SynthesisResult}`, returns `TraceMap`.
     * `POST /api/v3/export/slides`: accepts `PaperProject`, returns `SlideDeck`.
     * `GET /api/v3/export/slides/download`: accepts `paper_id: str`, returns `FileResponse` or `Response` with markdown attachment.
   - Function `register_v3_routes(app: FastAPI)` to include router.
2. File: `tests/test_v3_routes.py`
   - Unit tests using FastAPI `TestClient` testing citation graph, formula verification, transpilation, alignment, and slides endpoints.

Ensure clean code, type annotations, and robust error handling."""
    }
]

def main():
    print(f"Launching {len(TASKS)} parallel Jules v0.3.0 sessions for source: {SOURCE_NAME}...\n")
    results = []
    for idx, t in enumerate(TASKS, 1):
        print(f"[{idx}/{len(TASKS)}] Starting task: {t['title']}...")
        payload = {
            "prompt": t["prompt"],
            "sourceContext": {
                "source": SOURCE_NAME,
                "githubRepoContext": {
                    "startingBranch": "main"
                }
            },
            "title": t["title"],
            "automationMode": "AUTO_CREATE_PR"
        }
        try:
            r = requests.post("https://jules.googleapis.com/v1alpha/sessions", headers=HEADERS, json=payload, timeout=30)
            if r.status_code in (200, 201):
                data = r.json()
                sess_name = data.get("name") or data.get("id")
                print(f"  --> SUCCESS: Session created! ID: {sess_name}")
                results.append({"task_id": t["id"], "title": t["title"], "session": sess_name, "data": data})
            else:
                print(f"  --> FAILED: HTTP {r.status_code} - {r.text[:300]}")
                results.append({"task_id": t["id"], "title": t["title"], "error": r.text})
        except Exception as e:
            print(f"  --> EXCEPTION: {e}")
            results.append({"task_id": t["id"], "title": t["title"], "error": str(e)})
        time.sleep(1)

    # Save session tracking info to disk
    os.makedirs(".jules", exist_ok=True)
    with open(".jules/active_sessions_v3.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted! Active v0.3.0 sessions recorded in .jules/active_sessions_v3.json")

if __name__ == "__main__":
    main()
