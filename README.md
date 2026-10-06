# 📚 PaperAgent

> **AI-powered academic paper deep-reader, formula demystifier, and algorithm-to-executable-code synthesizer.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🚀 Key Highlights

* **📑 Multi-Source Ingestion**: Directly input ArXiv URLs / IDs (e.g. `2312.12456`), local PDFs, or cloud-parsed documents via Mineru.
* **🧠 Deep-Reading & Executive Brief**:
  - **Executive Summary**: 3-minute executive synthesis of problem, breakthrough, and empirical gains.
  - **Formula Demystifier**: Translates complex LaTeX mathematical equations into intuitive plain-language analogies and variable glossaries.
  - **Critic Reviewer Mode**: Top-tier conference (NeurIPS/ICLR) critique pointing out hidden assumptions, unproven claims, and missing baseline comparisons.
* **⚡ Algorithm-to-Code Synthesizer**:
  - Automatically identifies paper algorithms and pseudocode blocks.
  - Synthesizes self-contained, well-commented Python implementations with minimal dependencies.
  - Generates automated PyTest verification suites with synthetic toy datasets.
* **🛡️ Subprocess Execution Sandbox**:
  - Runs synthesized reproduction code safely with strict timeout & output isolation.
  - Captures terminal output, error traces, and rendered matplotlib plots.
* **🖥️ Dual-Pane Modern UI & Rich CLI**:
  - **CLI**: Fast terminal inspection with Rich tables, syntax highlighting, and progress bars.
  - **Web Dashboard**: Interactive split-screen layout (left: Paper structure & formulas, right: AI analysis, code editor, and live execution console).
* **📓 Export Anywhere**: Export complete findings to structured Markdown reports, BibTeX entries, or runnable Jupyter Notebooks (`.ipynb`).

---

## 🛠️ Quick Start

### 1. Installation

```bash
git clone https://github.com/ausyeah/PaperAgent.git
cd PaperAgent
pip install -r requirements.txt
pip install -e .
```

### 2. Configure Environment

Set your preferred LLM API key (supports Gemini, OpenAI, and compatible endpoints):

```bash
export GEMINI_API_KEY="your-gemini-api-key"
# Optional: Mineru API for high-fidelity OCR & table extraction
export MINERU_API_KEY="your-mineru-api-key"
```

### 3. Usage

#### CLI Mode
```bash
# Parse an ArXiv paper
paperagent parse 2312.12456

# Run full deep-reading analysis
paperagent analyze 2312.12456

# Synthesize runnable Python code from paper algorithms
paperagent synthesize 2312.12456

# Run the synthesized code in sandbox
paperagent run 2312.12456
```

#### Web Dashboard
```bash
paperagent serve --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for full module specifications and design guidelines.

```
PaperAgent/
├── paperagent/
│   ├── config.py           # Configuration & credentials
│   ├── models.py           # Core Pydantic data schemas
│   ├── parser/             # ArXiv, PDF, and Mineru extraction
│   ├── engine/             # LLM reasoning, formula explainer & reviewer
│   ├── synthesizer/        # Code synthesis, test generator, notebook export
│   ├── runner/             # Subprocess execution sandbox
│   ├── web/                # FastAPI application & single-page UI
│   └── cli.py              # Rich CLI commands
└── tests/                  # Pytest test suites
```

---

## 📄 License

MIT License. Developed by [ausyeah](https://github.com/ausyeah).
