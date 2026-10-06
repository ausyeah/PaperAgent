import os
import requests
import json

token = os.environ.get("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

repo = "ausyeah/PaperAgent"

release_notes = """# 🚀 PaperAgent v0.1.0 Release

Welcome to the initial release of **PaperAgent** — an AI-powered academic paper deep-reader, mathematical formula demystifier, and algorithm-to-executable-code synthesizer.

---

## 🌟 What's New in v0.1.0

### 📑 1. Multi-Source Paper Ingestion (`paperagent.parser`)
* **ArXiv Resolver & Downloader**: Parses ArXiv IDs (`2312.12456`, versioned IDs, URLs) and fetches official metadata directly via ArXiv Export API.
* **Layout & Formula Parser**: Extracts text sections, LaTeX equations (`$...$`, `$$...$$`, `\\begin{equation}`), and pseudocode blocks using pure Python (`pypdf`).
* **MinerU Cloud Adapter**: High-fidelity OCR & table extraction adapter for complex multi-column scientific layouts.

### 🧠 2. Unified LLM Gateway & Deep-Reading Engine (`paperagent.engine`)
* **Multi-Provider Client**: Native support for **Google Gemini 3.1 Pro** (`v1beta`) and standard OpenAI-compatible endpoints with streaming & JSON schema validation.
* **Resilient Offline Mock Mode**: Dynamic Pydantic schema traverser (`$defs` support) for offline testing without API keys.
* **Executive Brief**: 3-minute executive synthesis of problem statement, core trick, and methodology breakdown.
* **Formula Demystifier**: Translates dense mathematical equations into variable glossaries, analogies, and step-by-step intuitive explanations.
* **NeurIPS/ICLR Reviewer Critique**: Simulates top-tier area chairs evaluating novelties, hidden assumptions, failure modes, and assigning a 1-10 recommendation score.

### ⚡ 3. Algorithm-to-Code Synthesizer & Test Generator (`paperagent.synthesizer`)
* **Code Synthesizer**: Converts paper algorithms and formulas into clean, self-contained Python modules with NumPy and type hints.
* **Automated Test Generator**: Synthesizes companion PyTest verification test suites with synthetic toy datasets and mathematical invariant checks.

### 🛡️ 4. Safe Subprocess Execution Sandbox (`paperagent.runner`)
* Isolated temporary execution directories with strict timeout enforcement (`sandbox_timeout_seconds`).
* Captures `stdout`, `stderr`, exit codes, execution times, and generated artifact images (`.png` charts).

### 📓 5. Export Suite (`paperagent.export`)
* **Markdown**: Full formatted reading report with tables and KaTeX math blocks.
* **Jupyter Notebook (`.ipynb`)**: Runnable notebook combining narrative insights, formulas, synthesized code, and test executions.
* **BibTeX**: Standardized citation generation.

### 🖥️ 6. Modern Web Dashboard & Rich CLI (`paperagent.web` & `paperagent.cli`)
* **Rich CLI**: Beautiful terminal commands (`paperagent parse`, `analyze`, `synthesize`, `run`, `serve`).
* **Dual-Pane Web UI**: Sleek browser workstation featuring Paper outline on the left and 3-tab workstation (Executive Brief, Formula Cards, Code Editor + Live Terminal Runner) on the right.

---

## 🧪 Quality & Test Coverage
* **51 passing automated unit and integration tests** covering all modules end-to-end.
* Continuous Integration (CI) with GitHub Actions on Python 3.10 and 3.11.

---

Developed collaboratively with Google Jules (Gemini 3.1 Pro) across 8 concurrent development sessions.
"""

payload = {
    "tag_name": "v0.1.0",
    "target_commitish": "main",
    "name": "PaperAgent v0.1.0 - AI Paper Deep-Reader & Code Synthesizer",
    "body": release_notes,
    "draft": False,
    "prerelease": False
}

r = requests.post(f"https://api.github.com/repos/{repo}/releases", headers=headers, json=payload)
print("Release status:", r.status_code)
if r.status_code in (200, 201):
    data = r.json()
    print("Release URL:", data.get("html_url"))
else:
    print("Error:", r.text)
