"""
Script to launch 10 concurrent Jules coding sessions for PaperAgent v0.4.0.
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
        "id": "task_1_ablation_synthesizer",
        "title": "feat(synthesizer): implement automated ablation study generator and benchmark harness",
        "prompt": """Task: Implement Automated Ablation Study Generator in `paperagent/synthesizer/ablation.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `AblationVariant` and `AblationStudyResult` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/ablation.py`
   - Function / Class `AblationGenerator`:
     * `design_ablation_study(self, project: PaperProject, client: Optional[LLMClient] = None) -> AblationStudyResult`:
       Analyzes synthesized code and paper methodology.
       Generates 3 to 5 ablation variants (e.g., removing normalization, swapping positional embeddings, disabling residual/skip connections, replacing attention mechanisms).
       Each `AblationVariant` includes `variant_name`, `modified_component`, `hypothesis`, `code_modification`, `expected_impact`, and estimated `metrics`.
       Generates runnable `ablation_harness_code` that runs each variant and compares validation metrics.
       Provides `insights_summary` analyzing which components contribute most to empirical performance.
     * Robust offline fallback when LLM is unavailable or offline: generates sensible ablation variants based on standard deep learning components.
2. File: `tests/test_ablation.py`
   - Unit tests verifying `design_ablation_study` with mock project in offline and mocked LLM modes.
   - Asserts valid `AblationStudyResult`, presence of multiple variants, and non-empty harness code.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_2_literature_survey",
        "title": "feat(engine): implement deep literature survey and related works synthesis engine",
        "prompt": """Task: Implement Literature Survey Engine in `paperagent/engine/survey.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `LiteratureSurvey` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/survey.py`
   - Function / Class `LiteratureSurveyEngine`:
     * `synthesize_literature_survey(self, topic: str, papers: List[ParsedPaper], client: Optional[LLMClient] = None) -> LiteratureSurvey`:
       Organizes input papers and bibliography into a hierarchical `taxonomy_tree` (Dict[str, List[str]]).
       Builds a chronological milestone timeline (`chronology`: List of dicts with year, title, breakthrough).
       Builds a `comparative_table` comparing models across supervision type, compute complexity, and primary benchmark.
       Lists key `open_challenges` in the research field.
       Generates a structured `survey_markdown` comprehensive survey review.
     * Offline fallback generating a structured baseline survey when LLM is absent.
2. File: `tests/test_survey.py`
   - Unit tests verifying taxonomy generation, chronology ordering, comparative table structure, and markdown survey text.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_3_hardware_estimator",
        "title": "feat(synthesizer): implement hardware VRAM estimator and Optuna hyperparameter tuning harness",
        "prompt": """Task: Implement Hardware & Hyperparameter Estimator in `paperagent/synthesizer/hardware_estimator.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `HardwareProfile` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/hardware_estimator.py`
   - Function / Class `HardwareEstimator`:
     * `estimate_hardware_profile(self, project: PaperProject, param_count_m: Optional[float] = None) -> HardwareProfile`:
       Infers or calculates model parameter count (in millions).
       Estimates inference VRAM (MB) across sequence context lengths (e.g. '1k_ctx', '4k_ctx', '32k_ctx', '128k_ctx') accounting for weight memory and KV-cache scaling.
       Estimates training VRAM (MB) for optimizer states (AdamW), gradients, and activations with standard mixed precision (FP16/BF16).
       Recommends suitable GPU hardware (`recommended_gpu`, e.g., 'NVIDIA RTX 4090 (24GB)', 'NVIDIA A100 (80GB)', or 'Multi-H100 Cluster').
       Generates a clean Optuna hyperparameter tuning template (`optuna_hparam_search_code`) optimizing learning rate, batch size, and weight decay.
     * Fully deterministic mathematical formula modeling with optional paper parameter text parsing.
2. File: `tests/test_hardware_estimator.py`
   - Unit tests verifying memory calculations, GPU recommendations, and valid Optuna code syntax.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_4_meta_analysis",
        "title": "feat(engine): implement multi-paper consensus and cross-validation meta-analysis engine",
        "prompt": """Task: Implement Multi-Paper Meta-Analysis & Consensus Engine in `paperagent/engine/meta_analysis.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `ConsensusClaim` and `MetaAnalysisReport` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/meta_analysis.py`
   - Function / Class `MetaAnalysisEngine`:
     * `analyze_multi_paper_consensus(self, topic: str, projects: List[PaperProject], client: Optional[LLMClient] = None) -> MetaAnalysisReport`:
       Cross-examines claims and empirical findings across 2 or more paper projects.
       Identifies shared claims, supporting papers, and opposing/conflicting findings.
       Assigns `consensus_verdict` ('supported', 'contested', 'refuted', or 'insufficient_evidence') and provides `nuance_analysis`.
       Produces `overall_consensus_summary` giving an executive synthesis of empirical consensus in the literature.
     * Robust offline fallback when LLM is unavailable or offline.
2. File: `tests/test_meta_analysis.py`
   - Unit tests testing consensus resolution on mock papers with aligned and conflicting claims.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_5_environment_bundle",
        "title": "feat(export): implement hermetic Conda and CUDA Dockerfile reproduction environment exporter",
        "prompt": """Task: Implement Hermetic Environment Exporter in `paperagent/export/environment.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `EnvironmentBundle` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/environment.py`
   - Functions:
     * `generate_environment_bundle(project: PaperProject, python_version: str = "3.10", cuda_version: str = "12.1") -> EnvironmentBundle`:
       Analyzes synthesized code dependencies (torch, numpy, scipy, etc.) and paper metadata.
       Generates standard `conda_yaml` (environment.yml with channels conda-forge, pytorch, nvidia).
       Generates GPU-accelerated `dockerfile_cuda` based on `nvidia/cuda:12.1.0-runtime-ubuntu22.04` with Python and required dependencies.
       Generates `requirements_txt` with pinned compatible versions.
       Generates automated reproduction scripts: `reproduction_script_sh` (bash) and `reproduction_script_ps1` (powershell) to run tests and benchmarks.
     * `export_environment_bundle(project: PaperProject, output_dir: str) -> str`:
       Writes all environment files into `output_dir` and returns directory path.
2. File: `tests/test_environment_export.py`
   - Unit tests verifying generated YAML, Dockerfile, scripts, and file export in temporary directory.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_6_paper_qa",
        "title": "feat(engine): implement conversational paper QA assistant with grounded section and formula citations",
        "prompt": """Task: Implement Grounded Conversational Paper QA in `paperagent/engine/paper_qa.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `GroundedCitation` and `QAResponse` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/paper_qa.py`
   - Class `PaperQAAgent`:
     * `__init__(self, llm_client: Optional[LLMClient] = None)`
     * `answer_question(self, query: str, project: PaperProject) -> QAResponse`:
       Retrieves candidate sections and formulas from `project.paper` relevant to `query`.
       Drafts concise, authoritative answer.
       Attaches `GroundedCitation` items including `section_title`, optional `formula_id`, and `relevant_quote`.
       Computes `confidence_score` between 0.0 and 1.0.
     * Offline keyword-overlap / heuristic fallback when LLM is unavailable or offline.
2. File: `tests/test_paper_qa.py`
   - Unit tests verifying QA response structure, citation attribution, and offline fallback.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_7_audio_podcast",
        "title": "feat(export): implement two-host conversational academic podcast dialogue script generator",
        "prompt": """Task: Implement Academic Podcast Script Generator in `paperagent/export/audio_script.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `PodcastDialogueTurn` and `PodcastScript` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/export/audio_script.py`
   - Function / Class `generate_podcast_script(project: PaperProject, client: Optional[LLMClient] = None) -> PodcastScript`:
     Transforms paper findings, formula intuition, and reviewer critique into an engaging two-person conversational podcast dialogue (NotebookLM style).
     Hosts: "Alex (Explorer)" (inquisitive, asks big-picture questions) and "Morgan (Specialist)" (deep domain technical expert).
     Produces 6-12 dialogue turns with timing annotations and emotional tone markers (e.g. 'excited', 'thoughtful', 'analytical').
     Computes `total_duration_minutes`.
     Generates `audio_briefing_markdown` with formatted transcript and audio production notes.
     * `export_podcast_script_file(project: PaperProject, output_path: str) -> str`:
       Writes markdown transcript to file and returns output path.
     * Robust offline fallback generating structured dialogue from project analysis summary.
2. File: `tests/test_audio_script.py`
   - Unit tests checking speaker alternation, timing estimates, markdown export, and non-empty dialogue turns.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_8_hf_adapter",
        "title": "feat(synthesizer): implement HuggingFace PreTrainedModel and PretrainedConfig adapter synthesizer",
        "prompt": """Task: Implement HuggingFace Model Adapter Synthesizer in `paperagent/synthesizer/hf_adapter.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `HuggingFaceAdapterResult` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/synthesizer/hf_adapter.py`
   - Function / Class `synthesize_hf_adapter(project: PaperProject, client: Optional[LLMClient] = None) -> HuggingFaceAdapterResult`:
     Takes synthesized PyTorch code from `project.synthesis` and wraps it into idiomatic HuggingFace classes:
     - Subclass of `transformers.PretrainedConfig` (with model hyperparameters).
     - Subclass of `transformers.PreTrainedModel` (with `config_class`, initialization, forward method returning ModelOutput dict, and `.from_pretrained()` compatibility).
     - Provides `example_usage_code` showing how to initialize, save, and reload using `from_pretrained`.
     * Offline fallback generating standard clean HuggingFace boilerplate classes if LLM is offline or in mock mode.
2. File: `tests/test_hf_adapter.py`
   - Unit tests checking class definitions, AST validity of generated python code, and adapter result structure.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_9_author_rebuttal",
        "title": "feat(engine): implement top-tier conference author rebuttal and review response drafter",
        "prompt": """Task: Implement Author Rebuttal Drafter in `paperagent/engine/rebuttal.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Models `RebuttalPoint` and `RebuttalLetter` are defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/rebuttal.py`
   - Function / Class `AuthorRebuttalDrafter`:
     * `draft_author_rebuttal(self, project: PaperProject, review: Optional[OpenReviewReport] = None, client: Optional[LLMClient] = None) -> RebuttalLetter`:
       Analyzes reviewer weaknesses and negative critiques (from `review` or `project.analysis.reviewer_critique`).
       Drafts point-by-point rebuttals (`RebuttalPoint`) addressing each critique with:
         - `response_strategy` (e.g. 'Clarification', 'Additional Experiment', 'Theoretical Justification').
         - `detailed_rebuttal` with polite, scholarly tone acknowledging feedback while defending merits.
         - `proposed_new_experiments` with concrete ablation/baseline additions.
       Compiles complete `markdown_letter` ready for submission to OpenReview.
     * Offline fallback drafting standard scholarly rebuttal points.
2. File: `tests/test_rebuttal.py`
   - Unit tests verifying point extraction, rebuttal tone, markdown letter formatting, and offline fallback.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_10_arxiv_radar",
        "title": "feat(storage): implement ArXiv daily radar and watchlist semantic monitor",
        "prompt": """Task: Implement ArXiv Daily Radar in `paperagent/storage/radar.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `DailyDigestReport` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/storage/radar.py`
   - Class `ArxivRadar`:
     * `__init__(self, vector_index: Optional[Any] = None)`
     * `generate_daily_digest(self, category_or_query: str, candidate_papers: List[Dict[str, Any]], top_k: int = 5) -> DailyDigestReport`:
       Ranks incoming ArXiv feed candidate papers based on keyword relevance or BM25 vector index score.
       Selects top-k most relevant papers.
       Produces structured `matched_papers` with relevance scores and TLDRs.
       Synthesizes `executive_briefing` summarizing the day's key research trends and breakthroughs in that topic.
     * Fully deterministic offline execution and unit testing without network dependence.
2. File: `tests/test_radar.py`
   - Unit tests verifying candidate scoring, top-k ranking, executive briefing generation, and empty candidate edge cases.

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
    print(f"Starting launch of {len(TASKS)} parallel Jules v4 sessions...")
    active_sessions = []
    
    for task in TASKS:
        sess = create_session(task)
        if sess:
            active_sessions.append(sess)
        time.sleep(1) # brief pacing between API calls
        
    os.makedirs(".jules", exist_ok=True)
    with open(".jules/active_sessions_v4.json", "w", encoding="utf-8") as f:
        json.dump(active_sessions, f, indent=2)
        
    print(f"\nSuccessfully launched {len(active_sessions)}/{len(TASKS)} Jules sessions.")
    print("Session info saved to .jules/active_sessions_v4.json")

if __name__ == "__main__":
    main()
