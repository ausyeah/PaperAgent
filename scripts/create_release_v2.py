import os
import httpx
import json

token = os.environ.get("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

repo = "ausyeah/PaperAgent"

release_notes = """# 🚀 PaperAgent v0.2.0 Release

We are proud to announce **PaperAgent v0.2.0** — a major feature release expanding PaperAgent into a comprehensive academic intelligence workstation with persistent paper management, multi-paper comparative analysis, NeurIPS/ICLR OpenReview peer reviewing, architecture visualization, and live streaming execution!

---

## 🌟 What's New in v0.2.0

### 📚 1. Persistent Paper Library & SQLite Storage (`paperagent.storage`)
* **SQLite Storage Layer**: Persistent storage for all parsed papers, analysis reports, and code syntheses (`~/.paperagent/library.db` or configurable URI/path).
* **Search & Tagging**: Full case-insensitive search across titles, summaries, and ArXiv IDs, with tag filtering and pagination.
* **REST CRUD Endpoints**: Integrated into `/api/library` for seamless saving, listing, loading, and deletion.

### 🌐 2. High-Fidelity ArXiv HTML Parser (`paperagent.parser.arxiv_html`)
* **ArXiv Experimental HTML Extraction**: Ingests papers directly from `https://arxiv.org/html/{id}`.
* **Pristine LaTeX & MathML**: Extracts exact LaTeX code directly from `alttext` attributes on `<math>` elements.
* **Algorithm Extraction**: Parses structured `<figure class="ltx_algorithm">` blocks with automatic fallback to PDF extraction if HTML is unavailable.

### ⚖️ 3. Multi-Paper Comparative Intelligence (`paperagent.engine.comparator`)
* **Head-to-Head Comparison**: Compares two papers across problem formulation, inductive bias, algorithmic complexity (time & memory), empirical benchmarks, and hardware demands.
* **Actionable Trade-Off Matrix**: Outputs structured `ComparisonMatrix` providing engineers with concrete guidance on when to choose Paper A vs Paper B.

### 🎓 4. NeurIPS / ICLR OpenReview Peer Reviewer (`paperagent.engine.openreview`)
* **Area Chair Grade Critique**: Simulates rigorous top-tier conference peer review (`OpenReviewReport`).
* **Scoring Metrics**: Detailed 1-4 scale scores for Soundness, Presentation, and Contribution, plus overall 1-10 recommendation score.
* **Critical Weaknesses & Rebuttal Questions**: Generates actionable weaknesses and probing rebuttal questions.
* **Reproducibility Checklist**: Automated verification of hyperparameters, dataset specifications, and code availability claims.

### 📊 5. Architecture Visualizer & Benchmark Plotter (`paperagent.synthesizer.visualizer`)
* **Mermaid Flowcharts**: Synthesizes clean Mermaid architecture diagrams depicting pipeline layers and data transformations.
* **Matplotlib Benchmark Scripts**: Generates executable Python plotting scripts and renders high-resolution `.png` benchmark charts.

### 📄 6. LaTeX Reproduction Package & Overleaf Exporter (`paperagent.export.latex`)
* **Complete LaTeX Article Source**: Formats paper summaries, formulas, and synthesized algorithms into compilable `main.tex`.
* **Overleaf Zip Bundle**: Generates a self-contained `.zip` archive containing `main.tex`, `references.bib`, `reproduction.py`, and `README.md` ready for instant Overleaf import.

### ⚡ 7. Asynchronous Live Streaming Runner (`paperagent.runner.streaming`)
* **Real-time SSE Output**: Emits live `stdout` and `stderr` execution events line-by-line during code execution.
* **Robust Process Lifecycle**: Cross-platform support with automated subprocess reaping and file-lock isolation on Windows.

### 🖥️ 8. Web UI v2 Upgrade (`paperagent.web.static`)
* **Modular Frontend**: Refactored into clean `app.js`, `style.css`, and `index.html`.
* **Paper Library Drawer**: Toggleable sidebar to search, load, and manage saved papers.
* **5-Tab Workstation**: Dedicated views for Deep Analysis, Formula Demystifier, OpenReview Score Cards, Synthesized Code & Live Console, and Architecture Visualizer.

### 🐳 9. Production Docker Deployment & Health Check (`paperagent.health`)
* **Diagnostic Endpoint `/healthz`**: Reports runtime health, memory, sandbox execution status, and LLM providers.
* **Container Ready**: Production `Dockerfile` and `docker-compose.yml` for one-command deployment.

---

## 🧪 Quality & Verification
* **84 / 84 passing automated tests** across all 14 submodules.
* Developed collaboratively using **Google Jules (Gemini 3.1 Pro)** across **10 concurrent development sessions** supervised and harmonized by **Antigravity (Gemini 3.8 Flash High)**.
"""

payload = {
    "tag_name": "v0.2.0",
    "target_commitish": "main",
    "name": "PaperAgent v0.2.0 - Paper Library, OpenReview Critique & Multi-Paper Comparator",
    "body": release_notes,
    "draft": False,
    "prerelease": False
}

with httpx.Client(timeout=15.0) as client:
    r = client.post(f"https://api.github.com/repos/{repo}/releases", headers=headers, json=payload)
    if r.status_code in (200, 201):
        rel = r.json()
        print(f"Release v0.2.0 created successfully!")
        print(f"URL: {rel.get('html_url')}")
    else:
        print(f"Error creating release: HTTP {r.status_code} - {r.text}")
