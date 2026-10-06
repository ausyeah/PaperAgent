# PaperAgent System Architecture & Development Guidelines

Welcome to **PaperAgent** — an AI-powered academic paper deep-reader, mathematical formula demystifier, and algorithm-to-executable-code synthesizer.

---

## 1. System Overview

PaperAgent takes academic papers (from ArXiv IDs, URLs, or local PDFs), decomposes them into semantic sections and mathematical formulas, generates in-depth researcher-grade analyses, synthesizes self-contained runnable Python reproductions of the paper's core algorithms, and provides an interactive dual-pane Web interface and CLI.

```
                      ┌──────────────────────┐
                      │  User Input (ArXiv / │
                      │      Local PDF)      │
                      └──────────┬───────────┘
                                 │
                                 ▼
                     ┌────────────────────────┐
                     │ 1. Paper Parser        │
                     │    (paperagent.parser) │
                     │    - ArXiv Downloader  │
                     │    - PDF / Mineru Extr │
                     │    - Formula Extractor │
                     └──────────┬─────────────┘
                                │ ParsedPaper
                                ▼
                     ┌────────────────────────┐
                     │ 2. AI Reasoning Engine │
                     │    (paperagent.engine) │
                     │    - Executive Summary │
                     │    - Formula Explainer │
                     │    - Peer Critic Mode  │
                     └──────────┬─────────────┘
                                │ AnalysisReport
                                ▼
                     ┌────────────────────────┐
                     │ 3. Code Synthesizer    │
                     │ (paperagent.synthesizer│
                     │    - Algorithm to Py   │
                     │    - Toy Benchmark Gen │
                     │    - Sandbox Runner    │
                     │    - Jupyter Exporter  │
                     └──────────┬─────────────┘
                                │ SynthesisResult
                                ▼
         ┌─────────────────────────────────────────────────┐
         │ 4. Presentation & Interaction                   │
         │    - CLI Commands (paperagent.cli)              │
         │    - Split-screen Web UI (paperagent.web)       │
         │    - Markdown & Notebook Export                 │
         └─────────────────────────────────────────────────┘
```

---

## 2. Module Specifications & Interfaces

### 2.1 Module 1: `paperagent.parser`
* **File Structure:**
  - `paperagent/parser/arxiv.py`: Downloads ArXiv paper metadata and PDF using ArXiv API / HTTP requests.
  - `paperagent/parser/pdf_extractor.py`: Extracts raw text, headings, sections, and LaTeX-style equations using `pypdf` / regex / heuristics.
  - `paperagent/parser/mineru_adapter.py`: Optional high-fidelity cloud parsing adapter if `MINERU_API_KEY` is present.
  - `paperagent/parser/__init__.py`: Exposes `parse_paper(source: str) -> ParsedPaper`.

### 2.2 Module 2: `paperagent.engine`
* **File Structure:**
  - `paperagent/engine/llm_client.py`: Multi-provider LLM gateway supporting Gemini (via Google AI API/OpenAI-compatible) and standard OpenAI-compatible endpoints with streaming & JSON mode.
  - `paperagent/engine/prompts.py`: Carefully tuned prompt templates for Executive Brief, Intuitive Formula Explainer, Peer-Reviewer Critique, and Pseudocode Extraction.
  - `paperagent/engine/analyzer.py`: Orchestrates reading workflows; converts a `ParsedPaper` into an `AnalysisReport`.

### 2.3 Module 3: `paperagent.synthesizer` & `paperagent.runner`
* **File Structure:**
  - `paperagent/synthesizer/code_generator.py`: Generates clean, well-commented, dependency-minimal Python code implementing the paper's core algorithm.
  - `paperagent/synthesizer/test_generator.py`: Generates accompanying PyTest test cases with synthetic toy datasets or assertions.
  - `paperagent/synthesizer/notebook_export.py`: Converts the paper insights, mathematical formulas, and synthesized code into a runnable `.ipynb` Jupyter Notebook.
  - `paperagent/runner/sandbox.py`: Safely executes generated code in a subprocess with timeouts, captures `stdout`, `stderr`, execution time, and any generated image artifacts (matplotlib figures).

### 2.4 Module 4: `paperagent.web` & `paperagent.cli`
* **File Structure:**
  - `paperagent/cli.py`: Modern terminal CLI with Rich progress bars, tables, and colored logs (`parse`, `analyze`, `synthesize`, `run`, `serve`).
  - `paperagent/web/app.py`: FastAPI backend exposing REST endpoints:
    - `POST /api/paper/parse`: Ingests ArXiv ID or uploaded PDF.
    - `POST /api/paper/analyze`: Triggers AI deep reading.
    - `POST /api/paper/synthesize`: Synthesizes code.
    - `POST /api/paper/run`: Executes the synthesized code and returns execution logs.
    - `GET /api/paper/export`: Downloads full report (Markdown or Jupyter Notebook).
  - `paperagent/web/static/`: Sleek, standalone single-page application with responsive split-screen layout (left: Paper view, right: AI analysis, formula cards, code editor, live console output).

### 2.5 Module 5: `paperagent.storage` (v0.2.0)
* **File Structure:**
  - `paperagent/storage/db.py`: SQLite-backed persistent repository for papers, analysis reports, and code syntheses. Exposes `PaperStorage` with CRUD operations (`save_paper`, `get_paper`, `list_papers`, `search_papers`, `delete_paper`).
  - `paperagent/storage/__init__.py`: Package entrypoint exporting `PaperStorage`.

### 2.6 Module 6: `paperagent.parser.arxiv_html` (v0.2.0)
* **File Structure:**
  - `paperagent/parser/arxiv_html.py`: High-fidelity ArXiv experimental HTML parser. Extracts pristine MathML/LaTeX equations and algorithm blocks directly from `https://arxiv.org/html/{arxiv_id}` using BeautifulSoup, with fallback to PDF extraction.

### 2.7 Module 7: `paperagent.engine.comparator` (v0.2.0)
* **File Structure:**
  - `paperagent/engine/comparator.py`: Cross-paper comparative intelligence. Compares two papers across complexity, assumptions, empirical gains, and hardware constraints, returning structured `ComparisonMatrix`.

### 2.8 Module 8: `paperagent.engine.openreview` (v0.2.0)
* **File Structure:**
  - `paperagent/engine/openreview.py`: NeurIPS/ICLR-standard peer reviewer engine. Generates structured `OpenReviewReport` evaluating soundness, presentation, contribution, critical weaknesses, and reproducibility checklist.

### 2.9 Module 9: `paperagent.synthesizer.visualizer` (v0.2.0)
* **File Structure:**
  - `paperagent/synthesizer/visualizer.py`: Generates Mermaid architecture/dataflow diagrams and self-contained Matplotlib benchmarking scripts, returning `List[DiagramArtifact]`.

### 2.10 Module 10: `paperagent.export.latex` (v0.2.0)
* **File Structure:**
  - `paperagent/export/latex.py`: Packages paper synthesis into a complete LaTeX reproduction bundle (`main.tex`, algorithm floats, references) ready for zip download and Overleaf compilation.

### 2.11 Module 11: `paperagent.runner.streaming` (v0.2.0)
* **File Structure:**
  - `paperagent/runner/streaming.py`: Live asynchronous line-by-line runner. Emits stdout/stderr events via AsyncGenerator for real-time Server-Sent Events (SSE) streaming.

### 2.12 Module 12: `paperagent.web.library_routes` (v0.2.0)
* **File Structure:**
  - `paperagent/web/library_routes.py`: REST router for persistent paper library, multi-paper comparison (`/api/compare`), and OpenReview generation (`/api/openreview`).

### 2.13 Module 13: `paperagent.health` & Deployment (v0.2.0)
* **File Structure:**
  - `paperagent/health.py`: Health check and system diagnostic endpoint (`/healthz`).
  - `Dockerfile` & `docker-compose.yml`: Containerized production deployment.

---

## 3. Data Flow & Shared Contracts
All modules share data models defined in `paperagent/models.py`.
- No module should bypass `models.py` when passing structured data.
- All errors should be caught and converted into informative messages or custom exceptions.

---

## 4. Testing & Code Quality
- All unit tests live in `tests/`.
- Every subpackage should have dedicated test coverage.
- Run tests via `pytest -v`.

