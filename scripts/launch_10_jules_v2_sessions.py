"""
Script to launch 10 concurrent Jules coding sessions for PaperAgent v0.2.0.
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
        "id": "task_1_storage",
        "title": "feat(storage): implement SQLite-backed paper library and search index",
        "prompt": """Task: Implement SQLite Paper Library & Storage in `paperagent/storage/db.py` and `paperagent/storage/__init__.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `PaperProject`, `StoredPaperRecord`, `ParsedPaper`, `AnalysisReport`, `SynthesisResult` are already defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/storage/db.py`
   - Class `PaperStorage`:
     * `__init__(self, db_path: Optional[str | Path] = None)`: Default to `Path.home() / ".paperagent" / "library.db"`. Creates parent directories and SQLite schema if not exists.
     * Table schema `papers`:
       `id TEXT PRIMARY KEY, title TEXT, arxiv_id TEXT, created_at TEXT, tags TEXT, summary TEXT, has_code INTEGER, parsed_json TEXT, analysis_json TEXT, synthesis_json TEXT`
     * `save_paper(self, project: PaperProject, tags: Optional[List[str]] = None) -> StoredPaperRecord`:
       Serializes the `PaperProject` (using Pydantic `.model_dump_json()`), sets `has_code=bool(project.synthesis and project.synthesis.implementation_code)`, inserts or replaces the row, and returns `StoredPaperRecord`.
     * `get_paper(self, paper_id: str) -> Optional[PaperProject]`:
       Fetches row by `id`, deserializes `parsed_json`, `analysis_json`, `synthesis_json` back into `PaperProject`. Returns `None` if not found.
     * `list_papers(self, limit: int = 50, offset: int = 0, tag: Optional[str] = None) -> List[StoredPaperRecord]`:
       Returns lightweight `StoredPaperRecord` list ordered by `created_at DESC`. If `tag` is specified, filters records where `tag` is in `tags`.
     * `search_papers(self, query: str, limit: int = 20) -> List[StoredPaperRecord]`:
       Case-insensitive LIKE search on `title`, `summary`, or `arxiv_id`.
     * `delete_paper(self, paper_id: str) -> bool`:
       Deletes paper by `id`, returns `True` if deleted, `False` otherwise.
2. File: `paperagent/storage/__init__.py`
   - Exports `PaperStorage`.
3. File: `tests/test_storage.py`
   - Unit tests using temporary directory or `":memory:"` database.
   - Tests save, get, list with tag filter, search, and delete.

Ensure clean code, type annotations, and robust error handling. Do not break existing files."""
    },
    {
        "id": "task_2_arxiv_html",
        "title": "feat(parser): implement high-fidelity ArXiv HTML math and algorithm extractor",
        "prompt": """Task: Implement ArXiv HTML Parser in `paperagent/parser/arxiv_html.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
ArXiv now provides experimental HTML versions for papers (`https://arxiv.org/html/{arxiv_id}`).

Requirements:
1. File: `paperagent/parser/arxiv_html.py`
   - `fetch_arxiv_html(arxiv_id: str, timeout: float = 15.0) -> Optional[str]`:
     Queries `https://arxiv.org/html/{arxiv_id}` using `httpx`. If status code is 200, returns HTML text; if 404 or request error, returns `None`.
   - `parse_arxiv_html(html_content: str, arxiv_id: str) -> ParsedPaper`:
     Uses `bs4` (`BeautifulSoup`) to extract:
     * Paper title: check `<h1 class="ltx_title">`, `h1.title`, or `<title>`.
     * Authors: check elements with class `ltx_author`, `.authors`, or `span.author`.
     * Abstract: check `<div class="ltx_abstract">` or section containing abstract.
     * Sections: iterate over `<section class="ltx_section">` or `<section>` tags; extract heading `<h2 class="ltx_title">` and paragraph contents into `PaperSection(title=..., content=...)`.
     * Formulas: search for `<math>`, `<span class="ltx_Math">`, or `<div class="ltx_equation">`. Extract LaTeX representation from attribute `alttext` or math text, creating `ExtractedFormula(latex=..., context=...)`.
     * Algorithms: search for algorithm floats (`<figure class="ltx_algorithm">`, `<div class="ltx_algorithm">`, or blocks containing "Algorithm"), creating `ExtractedAlgorithm(name=..., pseudocode=...)`.
     * Returns assembled `ParsedPaper(metadata=..., sections=..., formulas=..., algorithms=..., raw_text=...)`.
   - `extract_paper_from_arxiv_source(source: str) -> ParsedPaper`:
     Extracts ArXiv ID via `extract_arxiv_id(source)`. Tries `fetch_arxiv_html`. If HTML is found, returns `parse_arxiv_html(html, arxiv_id)`. If HTML is `None` (or 404), falls back to `paperagent.parser.arxiv.fetch_arxiv_metadata` and PDF parser (`parse_paper(source)`).
2. File: `tests/test_arxiv_html.py`
   - Unit tests using synthetic HTML fixtures containing sections, formulas with `alttext`, and algorithm blocks.
   - Tests extraction, parsing, and fallback logic with mocking.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_3_comparator",
        "title": "feat(engine): implement multi-paper comparative intelligence and trade-off analyzer",
        "prompt": """Task: Implement Multi-Paper Comparative Intelligence in `paperagent/engine/comparator.py`

Context:
See `ComparisonDimension` and `ComparisonMatrix` in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/comparator.py`
   - Class `PaperComparator`:
     * `__init__(self, llm_client: Optional[LLMClient] = None)`: uses `LLMClient` or instantiates default.
     * `async def compare_papers(self, paper_a: ParsedPaper, paper_b: ParsedPaper) -> ComparisonMatrix`:
       Generates structured comparison between Paper A and Paper B.
       Evaluates key dimensions:
         - Inductive Bias & Core Approach
         - Mathematical Formulation
         - Computational Complexity (Time & Memory)
         - Empirical Benchmarks & Datasets
         - Practical Deployment & Hardware Requirements
       Produces `ComparisonMatrix`:
         - `paper_a_title`: paper_a.metadata.title
         - `paper_b_title`: paper_b.metadata.title
         - `dimensions`: List[ComparisonDimension]
         - `trade_off_summary`: summary of fundamental trade-offs
         - `recommended_choice`: actionable guidance on which to use in which scenarios.
     * Synchronous wrapper: `def compare_papers_sync(self, paper_a: ParsedPaper, paper_b: ParsedPaper) -> ComparisonMatrix`.
     * Offline / Mock mode support: If LLM is in mock mode or returns invalid JSON, return a realistic high quality fallback `ComparisonMatrix`.
2. File: `tests/test_comparator.py`
   - Unit tests with mock LLM client and synthetic `ParsedPaper` instances.
   - Verify all fields of `ComparisonMatrix` are populated.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_4_openreview",
        "title": "feat(engine): implement NeurIPS/ICLR OpenReview reviewer and checklist evaluator",
        "prompt": """Task: Implement NeurIPS/ICLR OpenReview Reviewer in `paperagent/engine/openreview.py`

Context:
See `OpenReviewReport` in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/openreview.py`
   - Class `OpenReviewEvaluator`:
     * `__init__(self, llm_client: Optional[LLMClient] = None)`: uses `LLMClient` or instantiates default.
     * `async def evaluate_paper(self, paper: ParsedPaper) -> OpenReviewReport`:
       Emulates rigorous NeurIPS/ICLR Area Chair and Reviewer.
       Produces `OpenReviewReport`:
         - `paper_title`: paper.metadata.title
         - `summary_of_work`: crisp summary of key contributions and main claims.
         - `strengths`: list of technical strengths.
         - `weaknesses`: list of specific technical weaknesses (missing baselines, unaddressed edge cases, etc.).
         - `questions_for_authors`: probing questions for the rebuttal phase.
         - `soundness_score`: int (1-4).
         - `presentation_score`: int (1-4).
         - `contribution_score`: int (1-4).
         - `overall_recommendation`: int (1-10).
         - `reproducibility_checklist_passed`: bool (whether code/hyperparameters/assumptions are specified).
     * Synchronous wrapper: `def evaluate_paper_sync(self, paper: ParsedPaper) -> OpenReviewReport`.
     * Offline / Mock mode support: realistic high quality mock report when LLM is offline or in mock mode.
2. File: `tests/test_openreview.py`
   - Unit tests verifying report structure, score bounds (scores between 1-4 and 1-10), and mock evaluation behavior.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_5_visualizer",
        "title": "feat(synthesizer): implement Mermaid architecture diagram and Matplotlib benchmark visualizer",
        "prompt": """Task: Implement Diagram & Visualizer Synthesizer in `paperagent/synthesizer/visualizer.py`

Context:
See `DiagramArtifact` in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/visualizer.py`
   - Class `VisualizerSynthesizer`:
     * `__init__(self, llm_client: Optional[LLMClient] = None)`
     * `generate_mermaid_architecture(self, paper: ParsedPaper) -> DiagramArtifact`:
       Produces a clean, valid Mermaid flowchart (`graph TD` or `flowchart TD`) representing the paper's model architecture or pipeline (nodes, arrows, tensor shapes/steps).
       Sets `diagram_type="mermaid"`, `title=f"{paper.metadata.title} - Architecture"`, `source_code=mermaid_str`.
     * `generate_matplotlib_benchmark(self, paper: ParsedPaper) -> DiagramArtifact`:
       Produces runnable Python script string using `matplotlib.pyplot` that plots a synthetic comparison benchmark (e.g. theoretical complexity vs sequence length, training loss curve, or throughput).
       Sets `diagram_type="matplotlib"`, `title=f"{paper.metadata.title} - Benchmark Plot"`, `source_code=script_str`.
     * `render_matplotlib_script(self, script_code: str, output_image_path: str) -> bool`:
       Executes the matplotlib code safely via Python subprocess or exec, ensuring `plt.savefig(output_image_path)` is called and the image is generated. Returns True if file was created, False otherwise.
     * Offline / Mock mode fallback with pre-baked valid Mermaid and Matplotlib templates.
2. File: `tests/test_visualizer.py`
   - Unit tests verifying Mermaid syntax starts with `graph ` or `flowchart `, Matplotlib code contains `import matplotlib`, and script rendering works.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_6_latex_export",
        "title": "feat(export): implement LaTeX reproduction package and Overleaf zip exporter",
        "prompt": """Task: Implement LaTeX Package & Overleaf Zip Exporter in `paperagent/export/latex.py`

Context:
See `PaperProject` in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/latex.py`
   - `generate_latex_source(project: PaperProject) -> str`:
     Generates a clean, compilable LaTeX document (`main.tex`) using standard `\\documentclass{article}`:
     * Packages: `amsmath`, `amssymb`, `algorithm`, `algpseudocode`, `listings`, `hyperref`, `booktabs`.
     * Sections for Executive Summary, Mathematical Formulation, Extracted Algorithm, Python Implementation Code (`listings`), and Peer Review.
   - `generate_bibtex(project: PaperProject) -> str`:
     Generates valid BibTeX citation string.
   - `export_latex_bundle(project: PaperProject, output_zip_path: str) -> str`:
     Creates a `.zip` archive containing:
       * `main.tex`: complete LaTeX source.
       * `references.bib`: BibTeX citations.
       * `reproduction.py`: synthesized Python code (if present in `project.synthesis`).
       * `README.md`: Overleaf instructions & compilation guide.
     Returns the absolute path to the generated zip file.
2. File: `tests/test_latex_export.py`
   - Unit tests verifying LaTeX source contains required sections.
   - Unit tests verifying `export_latex_bundle` writes a valid zip file containing `main.tex`, `references.bib`, and `README.md`.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_7_streaming_runner",
        "title": "feat(runner): implement asynchronous live streaming runner for SSE execution logs",
        "prompt": """Task: Implement Live Streaming Sandbox Runner in `paperagent/runner/streaming.py`

Context:
See `paperagent/runner/sandbox.py`.

Requirements:
1. File: `paperagent/runner/streaming.py`
   - Class `StreamingSandboxRunner`:
     * `async def run_streaming(self, code: str, timeout: float = 30.0) -> AsyncGenerator[dict, None]`:
       Executes `code` in an asynchronous subprocess using `sys.executable` and `asyncio.create_subprocess_exec`.
       Streams output line-by-line as events:
       - Yields `{"event": "start", "timestamp": ...}`
       - For stdout lines: yields `{"event": "stdout", "data": line}`
       - For stderr lines: yields `{"event": "stderr", "data": line}`
       - On completion: yields `{"event": "done", "exit_code": returncode, "duration_seconds": duration}`
       - On timeout: cancels/kills process and yields `{"event": "timeout", "error": "Execution timed out"}`
     * Handles process cleanup (kills orphaned processes on cancellation or exception).
2. File: `tests/test_streaming.py`
   - Unit tests using `pytest-asyncio` / `asyncio`.
   - Test streaming stdout from `print("Hello"); print("World")`.
   - Test streaming stderr from `import sys; sys.stderr.write("Warn\\n")`.
   - Test timeout handling.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_8_library_api",
        "title": "feat(web): implement paper library CRUD, comparison, and OpenReview REST endpoints",
        "prompt": """Task: Implement Library and Extended REST Endpoints in `paperagent/web/library_routes.py`

Context:
See `paperagent/storage/` and `paperagent/models.py`.

Requirements:
1. File: `paperagent/web/library_routes.py`
   - FastAPI `router = APIRouter(prefix="/api", tags=["library"])`
   - Endpoints:
     * `GET /api/library`: query params `limit: int = 50, offset: int = 0, tag: Optional[str] = None, q: Optional[str] = None`. Uses `PaperStorage` to return list of `StoredPaperRecord`.
     * `GET /api/library/{paper_id}`: returns `PaperProject` or 404 if not found.
     * `POST /api/library`: accepts `PaperProject`, saves via `PaperStorage`, returns `StoredPaperRecord`.
     * `DELETE /api/library/{paper_id}`: deletes from storage, returns `{"status": "deleted", "id": paper_id}`.
     * `POST /api/compare`: accepts JSON `{"paper_a": ParsedPaper, "paper_b": ParsedPaper}`. Returns `ComparisonMatrix`.
     * `POST /api/openreview`: accepts `ParsedPaper`. Returns `OpenReviewReport`.
     * `GET /api/paper/export/latex`: accepts `paper_id` query param, returns zip download via `FileResponse` or `Response`.
   - Function `register_library_routes(app: FastAPI)` to include router.
2. File: `tests/test_library_api.py`
   - Unit tests using FastAPI `TestClient` testing CRUD operations, compare, and openreview endpoints.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_9_frontend_v2",
        "title": "feat(frontend): upgrade dual-pane Web UI with paper library drawer and OpenReview cards",
        "prompt": """Task: Upgrade Standalone Single-Page Web UI in `paperagent/web/static/`

Context:
See existing `paperagent/web/static/index.html`.

Requirements:
1. Maintain clean modern layout with zero external build tools required (pure HTML/CSS/JS with CDN KaTeX and Mermaid).
2. UI Additions:
   - Library Drawer / Bar: toggleable "Paper Library" drawer showing saved papers list, search bar, and "Load" / "Delete" buttons.
   - Workstation Tab Navigation (Right Pane):
     * Tab 1: "Analysis & Summary" (executive brief, problem statement, core insights).
     * Tab 2: "Formula Demystifier" (formula cards, intuition, variable glossary).
     * Tab 3: "OpenReview Report" (NeurIPS score badges: Soundness, Presentation, Contribution, Overall Score 1-10; Strengths & Weaknesses bullet points; Questions for Rebuttal).
     * Tab 4: "Executable Code & Runner" (code editor, "Run Code" button, live console log output).
     * Tab 5: "Architecture Visualizer" (Mermaid diagram viewer and Matplotlib benchmark chart preview).
     * Action Bar: "Export LaTeX Bundle (.zip)" button next to Markdown/Notebook exports.
   - Responsive styling with sleek dark/light theme accents and clean typography.
3. Files to update/create:
   - `paperagent/web/static/index.html`: updated layout and tabs.
   - `paperagent/web/static/style.css`: updated styling for library drawer, score badges, tabs, and layout.
   - `paperagent/web/static/app.js`: updated frontend logic connecting to `/api/library`, `/api/openreview`, `/api/compare`, and existing endpoints.

Ensure clean, standalone, responsive frontend without external node_modules or build steps."""
    },
    {
        "id": "task_10_deployment",
        "title": "feat(ops): add production Dockerfile, docker-compose, and health diagnostic endpoint",
        "prompt": """Task: Implement Health Diagnostics and Production Docker Deployment

Context:
See `ARCHITECTURE.md`.

Requirements:
1. File: `paperagent/health.py`
   - `check_system_health() -> dict`:
     Checks:
     * `status`: "healthy" or "degraded"
     * `version`: "0.2.0"
     * `python_version`: sys.version
     * `sandbox_available`: runs a trivial 1-line Python code test using `sys.executable` to verify subprocess execution capability.
     * `storage_dir_writable`: checks if cache/storage directory exists and is writable.
     * `configured_providers`: lists active providers (Gemini, OpenAI, or Mock fallback).
   - Exposes router or helper with `GET /healthz`.
2. File: `Dockerfile`
   - Based on `python:3.11-slim`.
   - Copies `requirements.txt` and installs dependencies.
   - Copies application source code.
   - Exposes port 8000.
   - Sets environment variables (`PYTHONUNBUFFERED=1`).
   - CMD `["uvicorn", "paperagent.web.app:app", "--host", "0.0.0.0", "--port", "8000"]`.
3. File: `docker-compose.yml`
   - Service `paperagent`:
     * build: `.`
     * ports: `8000:8000`
     * volumes: `paperagent-data:/root/.paperagent`
     * environment: passthrough for `GEMINI_API_KEY`, `OPENAI_API_KEY`, etc.
4. File: `tests/test_health.py`
   - Unit tests for `check_system_health()` verifying returned dictionary fields (`status`, `sandbox_available`, `version`).

Ensure clean code, type annotations, and robust error handling."""
    }
]

def main():
    print(f"Launching {len(TASKS)} parallel Jules v0.2.0 sessions for source: {SOURCE_NAME}...\n")
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
    with open(".jules/active_sessions_v2.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted! Active v0.2.0 sessions recorded in .jules/active_sessions_v2.json")

if __name__ == "__main__":
    main()
