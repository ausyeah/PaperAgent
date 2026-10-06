"""
Script to launch 8 concurrent Jules coding sessions for PaperAgent.
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
        "id": "task_1_arxiv",
        "title": "feat: implement ArXiv ingestion and metadata downloader",
        "prompt": """Task: Implement ArXiv Downloader & Resolver in `paperagent/parser/arxiv.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py` for contracts. All models (PaperMetadata, etc.) are already defined.

Requirements:
1. File: `paperagent/parser/arxiv.py`
   - `extract_arxiv_id(input_str: str) -> Optional[str]`: parses strings, handles pure IDs (e.g. '2312.12456', '2312.12456v2', 'math/0501001'), and ArXiv URLs (e.g. 'https://arxiv.org/abs/2312.12456', 'https://arxiv.org/pdf/2312.12456.pdf').
   - `fetch_arxiv_metadata(arxiv_id: str) -> PaperMetadata`: queries the ArXiv API (http://export.arxiv.org/api/query?id_list=...) and extracts title, authors, abstract, published year, categories, doi, and pdf_url.
   - `download_arxiv_pdf(arxiv_id: str, output_path: Optional[str] = None) -> str`: downloads the PDF using httpx or urllib, caches it locally under settings.cache_dir / f"{arxiv_id}.pdf", and returns the saved file path.
2. File: `tests/test_arxiv_parser.py`
   - Comprehensive unit tests (compatible with unittest and pytest).
   - Test ID extraction with various URL/string formats.
   - Mock ArXiv API XML response to test metadata extraction.
   - Mock PDF download with temporary files.

Ensure proper type hints, docstrings, and robust error handling. Do not break existing files."""
    },
    {
        "id": "task_2_pdf_parser",
        "title": "feat: implement PDF section, formula, and algorithm extraction",
        "prompt": """Task: Implement PDF Extractor & Formula/Algorithm Parser in `paperagent/parser/pdf_extractor.py` and `paperagent/parser/mineru_adapter.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`. Models `ExtractedFormula`, `ExtractedAlgorithm`, `PaperSection`, and `ParsedPaper` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/parser/pdf_extractor.py`
   - Uses `pypdf` (already in requirements.txt) to extract page-by-page text.
   - Clean header/footer artifacts and reconstruct markdown sections based on numeric/title patterns (e.g. "1. Introduction", "2. Related Work", "3. Methodology").
   - Extract mathematical formulas using regex heuristics (finds inline `$ ... $`, display `$$ ... $$`, `\\[ ... \\]`, and `\\begin{equation} ... \\end{equation}`), returning `List[ExtractedFormula]`.
   - Extract algorithm blocks (finds "Algorithm 1:", "Input:", "Output:", pseudocode blocks), returning `List[ExtractedAlgorithm]`.
   - Assembles into `ParsedPaper`.
2. File: `paperagent/parser/mineru_adapter.py`
   - Check `settings.mineru_api_key`. If set, provide an optional client that can call Mineru cloud API for PDF extraction. If no key or API fails, cleanly fallback to `pdf_extractor.py`.
3. File: `paperagent/parser/__init__.py`
   - Export `parse_paper(source: str) -> ParsedPaper` and helper functions. If source is an ArXiv ID or URL, delegate to arxiv downloader first.
4. File: `tests/test_pdf_parser.py`
   - Unit tests using mock PDF bytes or mock text strings to test section heading detection, equation extraction, and algorithm parsing.

Ensure proper type hints, docstrings, and compatibility with Python 3.10+."""
    },
    {
        "id": "task_3_llm_gateway",
        "title": "feat: implement unified LLM client gateway with Gemini and OpenAI support",
        "prompt": """Task: Implement Unified LLM Gateway in `paperagent/engine/llm_client.py`

Context:
See `ARCHITECTURE.md` and `paperagent/config.py`.

Requirements:
1. File: `paperagent/engine/llm_client.py`
   - Unified async and sync LLM client class `LLMClient`.
   - Native support for Google Gemini API (`https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`) using `settings.gemini_api_key`.
   - Support for standard OpenAI-compatible endpoints (`/v1/chat/completions`) using `settings.openai_api_key`.
   - Method `generate(prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False, temperature: float = 0.2) -> str`.
   - Method `generate_structured(prompt: str, response_model: Type[BaseModel], system_prompt: Optional[str] = None) -> BaseModel`: enforces or parses JSON response directly into the specified Pydantic model.
   - Retry logic with backoff for rate limits.
   - Offline / Mock fallback mode: when no API keys are configured, return realistic structured mock responses so the entire system can still be tested and demonstrated offline.
2. File: `tests/test_llm_client.py`
   - Unit tests for LLMClient (compatible with unittest and pytest).
   - Test JSON mode parsing, mock mode behavior, and error handling.

Ensure clean code, type annotations, and robust network error handling."""
    },
    {
        "id": "task_4_deep_reading",
        "title": "feat: implement AI deep-reading analyzer and NeurIPS critic reviewer",
        "prompt": """Task: Implement Deep-Reading Prompts & Analyzer in `paperagent/engine/`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`. Target models are `AnalysisReport`, `FormulaExplanation`, `ReviewerCritique`.

Requirements:
1. File: `paperagent/engine/prompts.py`
   - High quality prompt templates:
     a) `EXECUTIVE_SUMMARY_PROMPT`: produces executive summary, core problem, key innovation, and methodology overview.
     b) `FORMULA_EXPLAINER_PROMPT`: takes LaTeX formula and context, outputs variable glossary, intuitive intuition, and step-by-step breakdown.
     c) `REVIEWER_CRITIQUE_PROMPT`: simulates a top-tier conference (NeurIPS/ICLR) reviewer, evaluating strengths, weaknesses, hidden assumptions, failure modes, reproducibility pitfalls, and giving a 1-10 score.
2. File: `paperagent/engine/analyzer.py`
   - Class `PaperAnalyzer` with method `analyze(paper: ParsedPaper) -> AnalysisReport`.
   - Orchestrates LLM calls to generate summary, explain up to top 5 key formulas, and generate the reviewer critique.
   - Integrates with `paperagent.engine.llm_client.LLMClient`.
3. File: `paperagent/engine/__init__.py`
   - Export `PaperAnalyzer`, `analyze_paper`, and prompt constants.
4. File: `tests/test_analyzer.py`
   - Unit tests testing `PaperAnalyzer` with mocked LLM outputs, verifying `AnalysisReport` model fields and constraints.

Ensure thorough docstrings, clean typing, and graceful handling of empty paper sections."""
    },
    {
        "id": "task_5_codegen",
        "title": "feat: implement algorithm-to-code synthesizer and test generator",
        "prompt": """Task: Implement Code Synthesizer and Test Suite Generator in `paperagent/synthesizer/`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`. Target model is `SynthesisResult`.

Requirements:
1. File: `paperagent/synthesizer/code_generator.py`
   - Given an `ExtractedAlgorithm` or relevant paper methodology sections, prompt LLM to generate self-contained, high quality Python code implementing the core algorithm (`target_module_code`).
   - Code must:
     - Use only standard library and NumPy/PyTorch.
     - Include full type hints and docstrings.
     - Have an executable demonstration under `if __name__ == '__main__':` with synthetic toy data.
2. File: `paperagent/synthesizer/test_generator.py`
   - Generates accompanying automated test suite (`test_suite_code`) with unittest/pytest assertions verifying mathematical invariants, shape checks, and numerical stability.
3. File: `paperagent/synthesizer/__init__.py`
   - Class `CodeSynthesizer` with method `synthesize(paper: ParsedPaper, algo_index: int = 0) -> SynthesisResult`.
4. File: `tests/test_codegen.py`
   - Unit tests for code and test generator formatting, validating that generated code strings are valid Python syntax (using `ast.parse`).

Ensure clean modular design, type annotations, and solid unit tests."""
    },
    {
        "id": "task_6_sandbox",
        "title": "feat: implement safe subprocess execution sandbox and artifact capture",
        "prompt": """Task: Implement Subprocess Execution Sandbox in `paperagent/runner/`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`. Target model is `ExecutionResult`.

Requirements:
1. File: `paperagent/runner/sandbox.py`
   - Class `ExecutionSandbox`:
     - Method `run_code(code: str, timeout: int = 30) -> ExecutionResult`:
       * Creates an isolated temporary directory.
       * Writes the python code to `run_target.py`.
       * Executes `python run_target.py` in a separate subprocess.
       * Enforces execution timeout (`settings.sandbox_timeout_seconds`).
       * Captures `stdout`, `stderr`, exit code, execution time.
       * Scans the temporary directory for any generated artifact files (e.g. `.png`, `.jpg`, `.csv`, `.json`), copies them to `settings.output_dir`, and records their paths in `ExecutionResult.generated_artifacts`.
     - Method `run_tests(module_code: str, test_code: str, timeout: int = 30) -> ExecutionResult`:
       * Writes both module and test file into temp dir and executes `python -m unittest` or test runner, capturing pass/fail statistics.
2. File: `paperagent/runner/__init__.py`
   - Export `ExecutionSandbox` and standalone function `execute_code(...)`.
3. File: `tests/test_sandbox.py`
   - Unit tests verifying:
     - Successful execution with printed output.
     - Syntax error handling.
     - Subprocess timeout enforcement.
     - Artifact detection when a script saves a file.

Ensure Windows and Linux cross-platform compatibility, clean tempfile cleanup, and type hints."""
    },
    {
        "id": "task_7_export",
        "title": "feat: implement report exporter suite (Markdown, Jupyter Notebook, BibTeX)",
        "prompt": """Task: Implement Exporter Suite in `paperagent/export/`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/markdown.py`
   - `export_markdown(project: PaperProject) -> str`:
     - Formats complete reading report: Paper metadata header, Executive summary table, Section overview, Formula demystification cards with LaTeX math, NeurIPS Reviewer critique card with badge and scores, and synthesized Python code block.
2. File: `paperagent/export/notebook.py`
   - `export_jupyter_notebook(project: PaperProject, output_path: Optional[str] = None) -> str`:
     - Constructs a valid Jupyter Notebook JSON string (`.ipynb`, format v4).
     - Includes markdown cells for paper introduction and formula breakdown.
     - Includes code cells containing the synthesized algorithm code, test suite, and runnable toy demo.
     - Validates JSON format.
3. File: `paperagent/export/bibtex.py`
   - `generate_bibtex(meta: PaperMetadata) -> str`:
     - Generates standard BibTeX citation entry (@article{...}).
4. File: `paperagent/export/__init__.py`
   - Export `export_markdown`, `export_jupyter_notebook`, and `generate_bibtex`.
5. File: `tests/test_export.py`
   - Unit tests testing Markdown generation, valid Jupyter notebook JSON parsing (`json.loads`), and BibTeX syntax.

Ensure clean code, type annotations, and robust handling of optional fields."""
    },
    {
        "id": "task_8_web_cli",
        "title": "feat: implement interactive dual-pane Web UI and Rich CLI",
        "prompt": """Task: Implement Web Dashboard & Rich CLI in `paperagent/web/` and `paperagent/cli.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.

Requirements:
1. File: `paperagent/cli.py`
   - Terminal CLI powered by `rich` (console tables, syntax coloring, status spinners):
     - `parse <source>`: displays paper metadata, section outline, extracted formula count.
     - `analyze <source>`: displays Executive Brief, formula explanations, and Reviewer Critique with colored score badge.
     - `synthesize <source>`: displays synthesized Python code with syntax highlighting.
     - `run <source>`: executes code in sandbox and prints stdout/stderr.
     - `serve [--host 127.0.0.1] [--port 8000]`: runs the FastAPI server with uvicorn.
2. File: `paperagent/web/app.py`
   - FastAPI application with CORS and static file mounting:
     - `POST /api/paper/parse`: accepts JSON `{"source": "..."}` or file upload.
     - `POST /api/paper/analyze`: accepts `ParsedPaper`, returns `AnalysisReport`.
     - `POST /api/paper/synthesize`: accepts `ParsedPaper`, returns `SynthesisResult`.
     - `POST /api/paper/execute`: accepts `{"code": "..."}`, returns `ExecutionResult`.
     - `GET /api/paper/export/markdown`: downloads `.md`.
     - `GET /api/paper/export/notebook`: downloads `.ipynb`.
3. File: `paperagent/web/static/index.html` (self-contained, sleek modern CSS/JS):
   - Dual-pane layout:
     - Header: Input bar (ArXiv ID/URL or file drop), action buttons ("Parse", "Deep Analyze", "Synthesize Code").
     - Left Pane (Paper View): Title, authors, abstract, collapsible section navigation, and formula gallery.
     - Right Pane (Workstation):
       * Tab 1: Executive Brief & Reviewer Critique (with score badge 1-10, strengths, weaknesses).
       * Tab 2: Formula Demystifier (intuitive intuition, variable glossary).
       * Tab 3: Synthesized Code Editor & Live Subprocess Console (run code button, live stdout/stderr stream, artifact viewer).
4. File: `tests/test_web.py` and `tests/test_cli.py`:
   - Unit tests for FastAPI endpoints (using httpx or TestClient) and CLI argument parsing.

Ensure clean styling, responsive layout, and proper error handling."""
    }
]

def main():
    print(f"Launching {len(TASKS)} parallel Jules sessions for source: {SOURCE_NAME}...\n")
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
    with open(".jules/active_sessions.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nCompleted! Active sessions recorded in .jules/active_sessions.json")

if __name__ == "__main__":
    main()
