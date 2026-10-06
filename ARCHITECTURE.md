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

---

## 3. Data Flow & Shared Contracts
All modules share data models defined in `paperagent/models.py`.
- No module should bypass `models.py` when passing structured data.
- All errors should be caught and converted into informative messages or custom exceptions.

---

## 4. Testing & Code Quality
- All unit tests live in `tests/`.
- Every subpackage should have dedicated test coverage (`test_parser.py`, `test_engine.py`, `test_synthesizer.py`, `test_runner.py`, `test_web.py`).
- Run tests via `pytest -v`.
