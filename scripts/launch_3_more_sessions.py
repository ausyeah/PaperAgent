"""
Script to launch 3 additional Jules coding sessions (Tasks 13, 14, 15) to hit 15 concurrent sessions.
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
        "id": "task_13_reproduce_benchmark",
        "title": "feat(benchmarks): implement end-to-end seminal papers reproduction benchmark suite",
        "prompt": """Task: Implement Seminal Papers Reproduction Benchmark in `paperagent/benchmarks/reproduce_papers.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `BenchmarkEvaluationResult` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/benchmarks/reproduce_papers.py`
   - Class `PaperReproductionBenchmark`:
     * `benchmark_paper_reproduction(self, paper_name: str, code: str) -> BenchmarkEvaluationResult`:
       Executes reproducible baseline benchmarks for seminal algorithms:
         - 'Transformer' (Attention Is All You Need)
         - 'LoRA' (Low-Rank Adaptation)
         - 'Mamba' (Selective State Space Models)
       Measures throughput (samples/sec), execution time, and convergence/loss metrics.
       Returns `BenchmarkEvaluationResult`.
     * Fully deterministic offline benchmark execution.
2. File: `tests/test_reproduce_benchmark.py`
   - Unit tests testing the benchmark runner on synthetic implementations of Transformer, LoRA, and Mamba.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_14_speedup_comparator",
        "title": "feat(engine): implement cross-runtime speedup comparator for PyTorch, JAX, and Triton",
        "prompt": """Task: Implement Cross-Runtime Speedup Comparator in `paperagent/engine/speedup_comparator.py`

Context:
See `ARCHITECTURE.md` and `paperagent/models.py`.
Model `SpeedupComparisonResult` is defined in `paperagent/models.py`.

Requirements:
1. File: `paperagent/engine/speedup_comparator.py`
   - Class `SpeedupComparator`:
     * `compare_framework_runtimes(self, algorithm_name: str, input_shape: tuple = (16, 512, 64)) -> SpeedupComparisonResult`:
       Compares latency and throughput across PyTorch eager, JAX JIT, and Triton GPU kernels.
       Calculates speedup ratios relative to baseline PyTorch eager.
       Identifies `fastest_framework` and outputs `efficiency_notes`.
     * Deterministic calculation with heuristic fallback when specific GPU backends are not available locally.
2. File: `tests/test_speedup_comparator.py`
   - Unit tests verifying framework latency comparison, speedup calculations, and return model fields.

Ensure clean code, type annotations, and robust error handling."""
    },
    {
        "id": "task_15_web_ui_expansion",
        "title": "feat(web): expand single-page web dashboard with interactive committee and benchmark views",
        "prompt": """Task: Expand Web UI Dashboard in `paperagent/web/static/app.js` and `paperagent/web/static/index.html`

Context:
See `paperagent/web/static/` files and `paperagent/models.py`.

Requirements:
1. File: `paperagent/web/static/index.html`
   - Add tab headers and container panels for:
     - 'Peer Committee Review' (displays Reviewer 1, 2, 3 cards + Area Chair decision banner)
     - 'Reproducibility Scorecard' (displays 0-100 score circle + 10 criteria checklist)
     - 'Podcast Briefing' (displays two-host dialogue turns with speaker badges)
2. File: `paperagent/web/static/app.js`
   - Add frontend render functions:
     - `renderCommitteeReview(committeeData)`
     - `renderScorecard(scorecardData)`
     - `renderPodcast(podcastData)`
3. File: `tests/test_web_ui_expansion.py`
   - Unit tests verifying HTML structure, new container IDs (`tab-committee`, `tab-scorecard`, `tab-podcast`), and JS handler function existence.

Ensure clean code, type annotations, and robust error handling."""
    }
]

def main():
    print(f"Launching 3 additional Jules sessions to reach 15 concurrent sessions...")
    
    # Load existing active_sessions_v5
    active_path = ".jules/active_sessions_v5.json"
    with open(active_path, "r", encoding="utf-8") as f:
        existing = json.load(f)
        
    for task in TASKS:
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
        print(f"Launching {task['id']}...")
        res = requests.post(url, headers=HEADERS, json=body, timeout=30)
        if res.status_code in (200, 201):
            data = res.json()
            session_id = data.get("name", "").split("/")[-1]
            print(f"  -> SUCCESS: Session ID: {session_id}")
            existing.append({
                "task_id": task["id"],
                "title": task["title"],
                "session": data.get("name"),
                "session_name": data.get("name"),
                "session_id": session_id,
                "created_at": time.time()
            })
        else:
            print(f"  -> FAILED: HTTP {res.status_code}: {res.text}")
        time.sleep(1)
        
    with open(active_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)
        
    print(f"\nTotal active sessions in {active_path}: {len(existing)}")

if __name__ == "__main__":
    main()
