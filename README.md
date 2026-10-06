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
* **⚡ Multi-Framework Synthesizer & Transpiler**:
  - Synthesizes self-contained algorithm implementations across **NumPy, PyTorch (`nn.Module`), and JAX**.
  - Bidirectional **Code-to-Math Trace Aligner** links Python lines directly to paper formula IDs.
  - **HuggingFace Adapter Generator**: Wraps synthesized models in `PreTrainedModel` and `PretrainedConfig` classes with `.from_pretrained()` compatibility.
  - Generates automated PyTest verification suites with synthetic toy datasets.
* **🔬 Advanced Research Intelligence & Verification**:
  - **Automated Ablation Study Synthesizer**: Identifies architectural components, generates variants (no LayerNorm, no RoPE, etc.), and outputs comparison benchmarks.
  - **Empirical Profiler & Hardware Estimator**: Calculates KV-cache and training VRAM scaling across context lengths ($1k \dots 128k$), recommends GPUs, and generates Optuna tuning harnesses.
  - **Multi-Paper Meta-Analysis**: Cross-validates empirical claims across papers and diagnoses conflicting findings.
  - **Literature Survey Engine**: Synthesizes hierarchical taxonomy trees, chronological milestones, and comparative tables.
  - **Grounded Paper QA**: Multi-turn conversational research co-pilot citing exact section titles and formula IDs.
  - **Author Rebuttal Drafter**: Formulates point-by-point rebuttal letters and ablation action plans responding to peer review criticisms.
* **🌐 Lineage Graph & Semantic Radar**:
  - **Citation Graph**: Directed academic citation networks categorizing foundations, baselines, and successors.
  - **ArXiv Daily Radar**: Tracks research watchlists, computes BM25 relevance scores, and generates daily executive briefing digests.
* **🎙️ Multi-Channel Export, Podcasts & Containers**:
  - **Two-Host Academic Podcast**: Generates NotebookLM-style dialogue scripts between curious and expert hosts with timing annotations.
  - **Hermetic Reproduction Bundles**: Exports GPU-ready `Dockerfile.cuda`, Conda `environment.yml`, and reproduction scripts.
  - **Presentation Slides**: Generates presentation-ready **Marp** slide decks (`.md`) with LaTeX math and reviewer highlights.
  - **CI/CD Repro**: Standalone **GitHub Actions** CI workflows verifying paper implementations on every push.
* **🖥️ Multi-Modal Interface**:
  - **Rich TUI**: Full-screen interactive terminal dashboard with formula galleries and code viewer.
  - **Web Dashboard**: Split-screen single-page application with SSE live streaming execution console.
  - **REST API**: 30+ endpoints across v1, v2, v3, and v4 APIs.

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
