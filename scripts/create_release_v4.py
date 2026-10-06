import os
import httpx
import json

token = os.environ.get("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

repo = "ausyeah/PaperAgent"

release_notes = """# 🚀 PaperAgent v0.4.0 Release

We are thrilled to announce **PaperAgent v0.4.0** — our flagship release transforming PaperAgent into an enterprise-grade AI Academic Research Workstation and Autonomous Reproduction Lab!

This release introduces automated ablation studies, literature surveys, hardware VRAM & Optuna hyperparameter estimators, multi-paper meta-analysis, hermetic CUDA/Conda container bundles, grounded conversational paper QA with citations, NotebookLM-style two-host podcast scripts, HuggingFace Transformers adapters, top-tier conference author rebuttal drafters, and daily ArXiv semantic radar monitoring!

---

## 🌟 What's New in v0.4.0

### 🔬 1. Automated Ablation Study Synthesizer (`paperagent.synthesizer.ablation`)
* **Systematic Architectural Ablation**: Identifies core model building blocks (normalizations, rotary embeddings, skip connections, loss variants) and formulates 3-5 structured ablation variants (`AblationVariant`).
* **Automated Comparative Harness**: Generates runnable comparison scripts executing baseline and ablated models on toy benchmarks with delta metric tracking.

### 📚 2. Deep Literature Survey Engine (`paperagent.engine.survey`)
* **Hierarchical Taxonomies**: Organizes related works into structural categorization trees across methodology and supervision paradigms.
* **Chronological Milestones & Trade-off Tables**: Synthesizes year-by-year breakthrough timelines and feature comparison tables across computational complexity and benchmarks.
* **Open Challenges Analysis**: Surfaces persistent roadblocks and unsolved problems in the research field.

### ⚡ 3. Hardware Footprint & Optuna Hyperparameter Estimator (`paperagent.synthesizer.hardware_estimator`)
* **KV-Cache & Training VRAM Modeling**: Estimates GPU memory footprints across context lengths ($1k, 4k, 32k, 128k$) and optimizer states (AdamW mixed precision).
* **Hardware Sizing**: Recommends appropriate GPUs (RTX 4090, A100-80GB, or Multi-H100 clusters).
* **Optuna Harness**: Synthesizes clean hyperparameter optimization templates for automated trial pruning and tuning.

### ⚖️ 4. Multi-Paper Meta-Analysis & Consensus Engine (`paperagent.engine.meta_analysis`)
* **Cross-Validation of Literature Claims**: Cross-examines technical assertions across 2+ papers.
* **Consensus Verdicts**: Categorizes claims into `supported`, `contested`, `refuted`, or `insufficient_evidence` with nuanced condition reconciliations.

### 🐳 5. Hermetic Reproduction & Container Bundle Exporter (`paperagent.export.environment`)
* **Reproducibility Guarantee**: Analyzes synthesized code imports and produces complete environment bundles:
  - `environment.yml` for Conda environments
  - `Dockerfile` based on `nvidia/cuda:12.1.0-runtime-ubuntu22.04`
  - `requirements.txt` with pinned dependencies
  - Cross-platform reproduction runners: `reproduce.sh` (bash) and `reproduce.ps1` (PowerShell).

### 💬 6. Grounded Conversational Paper QA (`paperagent.engine.paper_qa`)
* **Strictly Grounded Answers**: Multi-turn conversational research co-pilot answering deep queries with `GroundedCitation` items citing exact section titles, formula IDs, and source text quotes.
* **Heuristic Offline Fallback**: Features intelligent token overlap search when offline.

### 🎙️ 7. NotebookLM-Style Two-Host Podcast Script Generator (`paperagent.export.audio_script`)
* **Dynamic Dialogue Production**: Generates natural, engaging scripts between two distinct personas: **Alex (Explorer)** (curious, high-level questioner) and **Morgan (Specialist)** (deep domain technical expert).
* **Audio Annotations**: Formatted with realistic second-by-second timing markers and emotional tone tags (e.g., `enthusiastic`, `analytical`, `thoughtful`).

### 🤗 8. HuggingFace Transformers Adapter Synthesizer (`paperagent.synthesizer.hf_adapter`)
* **Ecosystem Interoperability**: Converts synthesized PyTorch modules into idiomatic HuggingFace classes:
  - Subclasses of `transformers.PretrainedConfig`
  - Subclasses of `transformers.PreTrainedModel` with `.save_pretrained()` and `.from_pretrained()` support.

### ✍️ 9. Top-Tier Conference Author Rebuttal Drafter (`paperagent.engine.rebuttal`)
* **Area Chair Ready**: Ingests reviewer critiques and generates point-by-point rebuttal letters with response strategies (`Clarification`, `Additional Experiment`, `Theoretical Justification`) and concrete new experiment plans.

### 🛰️ 10. ArXiv Daily Radar & Semantic Watchlist Monitor (`paperagent.storage.radar`)
* **Automated Surveillance**: Monitors incoming ArXiv feeds against user research watchlists using the pure-Python BM25 vector index.
* **Executive Digest**: Ranks top-k breakthroughs and synthesizes daily executive briefing reports.

### 🔌 11. REST API v4 Expansion (`paperagent.web.v4_routes`)
* Exposes 10 new high-performance endpoints:
  - `POST /api/v4/ablation`
  - `POST /api/v4/survey`
  - `POST /api/v4/hardware`
  - `POST /api/v4/meta-analysis`
  - `POST /api/v4/environment`
  - `POST /api/v4/qa`
  - `POST /api/v4/podcast`
  - `POST /api/v4/hf-adapter`
  - `POST /api/v4/rebuttal`
  - `POST /api/v4/radar`

---

## 🧪 Quality & Verification Metrics
* **161 / 161 automated tests passing (100% pass rate)**.
* Built using the **Flash + Pro Collaborative Team Paradigm**:
  - Supervised, architected, harmonized, and verified by **Antigravity (Gemini 3.8 Flash High)**.
  - Implemented concurrently across **10 parallel Google Jules (Gemini 3.1 Pro)** sessions.
"""

payload = {
    "tag_name": "v0.4.0",
    "target_commitish": "main",
    "name": "PaperAgent v0.4.0 - Ablation Studies, Survey Engine, Hardware Estimator, Podcasts & Containers",
    "body": release_notes,
    "draft": False,
    "prerelease": False
}

with httpx.Client(timeout=15.0) as client:
    r = client.post(f"https://api.github.com/repos/{repo}/releases", headers=headers, json=payload)
    if r.status_code in (200, 201):
        rel = r.json()
        print(f"Release v0.4.0 created successfully!")
        print(f"URL: {rel.get('html_url')}")
    else:
        print(f"Error creating release: HTTP {r.status_code} - {r.text}")
