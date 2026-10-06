"""
Script to launch 12 concurrent Jules coding sessions for PaperAgent v0.5.0.
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
        "id": "task_1_triton_kernel",
        "title": "feat(synthesizer): implement GPU Triton kernel generator and benchmark harness",
        "prompt": """Task: Implement Triton GPU Kernel Synthesizer in `paperagent/synthesizer/kernel.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `TritonKernelResult` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/kernel.py`
   - Function / Class `TritonKernelSynthesizer`:
     * `synthesize_triton_kernel(self, project: PaperProject, client: Optional[LLMClient] = None) -> TritonKernelResult`:
       Synthesizes clean OpenAI Triton GPU kernel code (`@triton.jit`) for the paper's core operation (e.g., tiled matrix multiplication, fused softmax, or attention).
       Generates runnable `benchmark_harness_code` comparing Triton execution vs PyTorch eager execution.
       Estimates or measures `speedup_vs_eager`.
     * Robust offline fallback generating a valid fused matrix multiplication/attention Triton kernel when LLM is offline or mock mode.
2. File: `tests/test_kernel.py`
   - Unit tests checking generated Triton code syntax (AST validity) and `TritonKernelResult` attributes.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_2_peer_committee",
        "title": "feat(engine): implement multi-agent peer review committee and AC meta-review engine",
        "prompt": """Task: Implement Multi-Agent Peer Review Committee in `paperagent/engine/committee.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `IndividualReview` and `CommitteeReview` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/committee.py`
   - Class `PeerReviewCommittee`:
     * `evaluate_paper_committee(self, paper: ParsedPaper, client: Optional[LLMClient] = None) -> CommitteeReview`:
       Simulates a 3-reviewer conference review panel:
         - Reviewer 1: Theory Expert (evaluates mathematical rigor and proof foundations)
         - Reviewer 2: Empirical Skeptic (evaluates baselines, datasets, and ablation fairness)
         - Reviewer 3: Impact Champion (evaluates paradigm novelty and practical utility)
       Synthesizes Area Chair `meta_review` synthesizing reviews and assigning `final_decision` ('Accept (Oral)', 'Accept (Poster)', or 'Reject').
     * Offline fallback generating structured multi-persona reviews.
2. File: `tests/test_committee.py`
   - Unit tests verifying 3 reviews generated, diverse personas, score bounds (1-10), and valid decision.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_3_graph_view",
        "title": "feat(export): implement interactive D3 and vis.js citation lineage graph bundle exporter",
        "prompt": """Task: Implement Interactive Citation Graph Exporter in `paperagent/export/graph_view.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `CitationGraph` and `GraphVisualizationBundle` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/graph_view.py`
   - Function / Class `export_citation_graph_html(graph: CitationGraph, output_path: Optional[str] = None) -> GraphVisualizationBundle`:
     Converts `CitationGraph` nodes and edges into an interactive, physics-enabled HTML visualization bundle using vis.js or D3.js.
     Nodes are styled by role ('foundation' = blue, 'baseline' = orange, 'successor' = green).
     Includes interactive search filter and node detail sidebar.
     Returns `GraphVisualizationBundle(paper_title=..., nodes=..., edges=..., standalone_html=...)`.
     If `output_path` provided, writes HTML file to disk.
2. File: `tests/test_graph_view.py`
   - Unit tests checking node/edge mapping, HTML embedding of vis.js/D3 script, and file export.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_4_dataset_gen",
        "title": "feat(synthesizer): implement synthetic dataset generator and benchmark fixture synthesizer",
        "prompt": """Task: Implement Synthetic Dataset Fixture Generator in `paperagent/synthesizer/dataset_gen.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `SyntheticDatasetFixture` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/dataset_gen.py`
   - Class `SyntheticDatasetGenerator`:
     * `generate_dataset_fixture(self, project: PaperProject, num_samples: int = 1000) -> SyntheticDatasetFixture`:
       Synthesizes self-contained Python generator code producing realistic toy tensors/inputs matching paper dimension specs (e.g. sequences, masks, vocabulary distributions).
       Code includes PyTorch `Dataset` and `DataLoader` classes.
       Provides `sample_batch_summary` showing tensor shapes and statistics.
     * Fully offline deterministic code synthesis.
2. File: `tests/test_dataset_gen.py`
   - Unit tests checking generated code AST validity, execution in sandbox/exec, and shape assertions.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_5_quantizer",
        "title": "feat(synthesizer): implement post-training quantization and precision profiler",
        "prompt": """Task: Implement Quantization & Precision Profiler in `paperagent/synthesizer/quantizer.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `QuantizationBenchmarkRow` and `QuantizationProfile` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/quantizer.py`
   - Class `PrecisionQuantizer`:
     * `profile_quantization(self, project: PaperProject) -> QuantizationProfile`:
       Models and profiles model footprints across FP32, FP16, BF16, INT8, and INT4 precision.
       Calculates theoretical memory footprint (MB) and expected latency scaling.
       Generates PyTorch dynamic quantization wrapper code (`wrapper_code` using `torch.ao.quantization` or bitsandbytes stubs).
       Recommends optimal precision (`recommended_precision`).
     * Deterministic offline calculation.
2. File: `tests/test_quantizer.py`
   - Unit tests verifying precision table rows, memory reduction from FP32 to INT4, and valid wrapper code.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_6_scorecard",
        "title": "feat(engine): implement empirical reproducibility scorecard and checklist evaluator",
        "prompt": """Task: Implement Reproducibility Scorecard Evaluator in `paperagent/engine/scorecard.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `ReproducibilityScorecard` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/scorecard.py`
   - Class `ReproducibilityEvaluator`:
     * `evaluate_reproducibility(self, paper: ParsedPaper, client: Optional[LLMClient] = None) -> ReproducibilityScorecard`:
       Evaluates paper against 10 empirical reproducibility criteria:
         1. Code Repository URL Provided
         2. Dataset Availability & Licensing
         3. Hyperparameter Specification (LR, batch, epochs)
         4. Hardware Environment Specified (GPU type, count)
         5. Random Seed Reporting & Multiple Runs
         6. Error Bars / Standard Deviations Reported
         7. Compute Budget / Training Time Disclosed
         8. Evaluation Protocol Consistency
         9. Model Checkpoint Download Links
         10. Proof / Derivation Steps Clear
       Computes aggregate score (0-100), `verdict_level`, and actionable `improvement_recommendations`.
     * Offline heuristic fallback analyzing section text and regex patterns.
2. File: `tests/test_scorecard.py`
   - Unit tests verifying 10 criteria evaluated, score bounds, and recommendations.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_7_table_extractor",
        "title": "feat(parser): implement LaTeX and markdown table-to-CSV structured extractor",
        "prompt": """Task: Implement Structured Table Extractor in `paperagent/parser/table_extractor.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `ExtractedTable` and `ExtractedTableCollection` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/parser/table_extractor.py`
   - Class `TableExtractor`:
     * `extract_tables(self, paper: ParsedPaper) -> ExtractedTableCollection`:
       Parses paper text/markdown for markdown tables (`| col1 | col2 |`) and LaTeX `\\begin{table}` / `\\begin{tabular}` blocks.
       Extracts headers, table rows, and captions.
       Converts extracted tables into formatted CSV strings (`csv_data`).
     * Deterministic regex and parser implementation.
2. File: `tests/test_table_extractor.py`
   - Unit tests testing parsing of markdown tables and LaTeX tabular environments, verifying headers and CSV data.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_8_sync_bot",
        "title": "feat(export): implement automated Git PR and Overleaf reproduction sync bot",
        "prompt": """Task: Implement Reproduction Sync Bot in `paperagent/export/sync_bot.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `SyncBotBundle` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/sync_bot.py`
   - Function `create_reproduction_sync_bundle(project: PaperProject, target_repo: str = "org/repro") -> SyncBotBundle`:
     Constructs ready-to-use GitHub Pull Request content and automated git CLI commands:
     - Formats PR Title and markdown PR Body with reproduction summary, verification test badges, and hardware specs.
     - Generates sequence of git commands (branch creation, commit, remote push, and `gh pr create`).
2. File: `tests/test_sync_bot.py`
   - Unit tests checking PR body content, branch naming convention, and git command list.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_9_derivation",
        "title": "feat(engine): implement symbolic mathematical derivation and step-by-step verifier",
        "prompt": """Task: Implement Symbolic Derivation Verifier in `paperagent/engine/derivation.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `DerivationStep` and `DerivationVerificationResult` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/derivation.py`
   - Class `DerivationVerifier`:
     * `verify_derivation_steps(self, formula_from: ExtractedFormula, formula_to: ExtractedFormula, client: Optional[LLMClient] = None) -> DerivationVerificationResult`:
       Analyzes algebraic transition between two sequential formulas.
       Deconstructs transition into intermediate algebraic steps (`DerivationStep`).
       Checks mathematical soundness (`is_mathematically_sound`) and flags missing assumptions or dimensional jumps.
     * Offline fallback generating standard calculus/algebraic expansion steps.
2. File: `tests/test_derivation.py`
   - Unit tests verifying step sequence, soundness flag, and mathematical notes.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_10_tts_pipeline",
        "title": "feat(export): implement phonetic SSML audio podcast speech synthesizer pipeline",
        "prompt": """Task: Implement SSML Audio Speech Pipeline in `paperagent/export/tts_pipeline.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `PodcastScript` and `SSMLPodcastBundle` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/tts_pipeline.py`
   - Function `generate_ssml_podcast_bundle(script: PodcastScript) -> SSMLPodcastBundle`:
     Converts dialogue turns into standard W3C SSML (`<speak>`, `<voice>`, `<prosody>`, `<break>`).
     Replaces mathematical symbols with phonetic pronunciations (e.g., `\\theta` -> "theta", `\\mathcal{L}` -> "loss function L").
     Generates executable Python script (`tts_script_py`) compatible with edge-tts or pyttsx3 to render MP3 audio locally.
2. File: `tests/test_tts_pipeline.py`
   - Unit tests checking SSML XML tag validity, voice tag alternation, and phonetic replacements.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_11_clusterer",
        "title": "feat(storage): implement cross-paper semantic topic clustering and taxonomy mapper",
        "prompt": """Task: Implement Paper Library Clusterer in `paperagent/storage/clusterer.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `TopicCluster` and `TopicClusterCollection` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/storage/clusterer.py`
   - Class `PaperLibraryClusterer`:
     * `cluster_papers(self, papers: List[StoredPaperRecord], num_clusters: int = 3) -> TopicClusterCollection`:
       Clusters stored papers using TF-IDF / keyword co-occurrence without requiring external ML dependencies.
       Extracts top keywords representing each cluster.
       Groups paper IDs into appropriate `TopicCluster` entries.
       Generates cluster summaries.
     * Deterministic, zero-dependency pure Python clustering.
2. File: `tests/test_clusterer.py`
   - Unit tests clustering mock paper records into distinct thematic clusters with valid keywords.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_12_interactive_notebook",
        "title": "feat(export): implement interactive Jupyter notebook exporter with ipywidgets sliders",
        "prompt": """Task: Implement Interactive Notebook Exporter in `paperagent/export/interactive_notebook.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `InteractiveNotebookBundle` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/interactive_notebook.py`
   - Function `export_interactive_notebook(project: PaperProject, output_path: Optional[str] = None) -> InteractiveNotebookBundle`:
     Generates an advanced Jupyter notebook (`.ipynb`) with:
       - Mathematical Markdown cells with KaTeX equations.
       - Interactive ipywidgets sliders (e.g. sequence length, learning rate, temperature).
       - Live Matplotlib plots that update interactively based on slider inputs.
       - Synthesized core algorithm cells.
     Returns `InteractiveNotebookBundle(notebook_json=..., widget_features=..., file_path=...)`.
2. File: `tests/test_interactive_notebook.py`
   - Unit tests checking valid notebook JSON schema, widget imports, and file creation.

Ensure clean code, type annotations, and robust error handling."""
    }
]

def create_session(task):
    url = "https://jules.googleapis.com/v1alpha/sessions"
    body = {
        "sourceContext": {
            "source": SOURCE_NAME,
            "githubRepoContext": {
                "startingBranch": "main"
            }
        },
        "prompt": f"Title: {task['title']}\n\n{task['prompt']}"
    }
    
    print(f"Launching Jules session for {task['id']}...")
    res = requests.post(url, headers=HEADERS, json=body, timeout=30)
    if res.status_code in (200, 201):
        data = res.json()
        session_id = data.get("name", "").split("/")[-1]
        print(f"  -> SUCCESS: Session ID: {session_id} (Task: {task['id']})")
        return {
            "task_id": task["id"],
            "title": task["title"],
            "session": data.get("name"),
            "session_name": data.get("name"),
            "session_id": session_id,
            "created_at": time.time()
        }
    else:
        print(f"  -> FAILED: HTTP {res.status_code}: {res.text}")
        return None

def main():
    print(f"Starting launch of {len(TASKS)} parallel Jules v5 sessions...")
    active_sessions = []
    
    for task in TASKS:
        sess = create_session(task)
        if sess:
            active_sessions.append(sess)
        time.sleep(1) # brief pacing between API calls
        
    os.makedirs(".jules", exist_ok=True)
    with open(".jules/active_sessions_v5.json", "w", encoding="utf-8") as f:
        json.dump(active_sessions, f, indent=2)
        
    print(f"\nSuccessfully launched {len(active_sessions)}/{len(TASKS)} Jules sessions.")
    print("Session info saved to .jules/active_sessions_v5.json")

if __name__ == "__main__":
    main()
