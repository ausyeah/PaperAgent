from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from paperagent.web.app import app
from paperagent.models import (
    PaperProject,
    ParsedPaper,
    PaperMetadata,
    PaperSection,
    ExtractedFormula,
    ExtractedAlgorithm,
    SynthesisResult,
)

client = TestClient(app)

@pytest.fixture
def sample_project():
    metadata = PaperMetadata(
        title="Autonomous Evolutionary Deep Learning",
        authors=["Alice", "Bob"],
        abstract="We present an autonomous evolutionary learning framework.",
        arxiv_id="2402.00001",
        year=2024
    )
    formula = ExtractedFormula(
        id="eq-1",
        latex="y = \\sigma(Wx + b)",
        plain_explanation="Standard linear transform with activation."
    )
    algo = ExtractedAlgorithm(
        id="algo-1",
        name="EvolutionarySearch",
        pseudocode="1. Mutate\n2. Evaluate\n3. Select",
        inputs=["Population"],
        outputs=["Best"]
    )
    section = PaperSection(
        title="Methodology",
        level=1,
        content="We evaluate across architectures with ImageNet score 88.5% and latency 12ms.",
        formulas=[formula],
        algorithms=[algo]
    )
    paper = ParsedPaper(
        metadata=metadata,
        sections=[section],
        raw_markdown="# Autonomous Evolutionary Deep Learning\nOur methodology outperforms prior work.\n",
        source_type="arxiv"
    )
    synthesis = SynthesisResult(
        algorithm_name="EvolutionarySearch",
        target_module_code="def run(): return 42\n",
        test_suite_code="def test_run(): assert True\n"
    )
    return PaperProject(
        id="proj-v6",
        paper=paper,
        synthesis=synthesis,
        created_at=datetime.now(timezone.utc)
    )

def test_v6_hypothesis_endpoint(sample_project):
    payload = {"paper": sample_project.paper.model_dump(mode="json")}
    res = client.post("/api/v6/hypothesis", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["hypotheses"]) >= 1

def test_v6_self_heal_endpoint():
    payload = {"code": "x = np.array([1, 2, 3])\nprint(x.sum())", "max_iterations": 2}
    res = client.post("/api/v6/self-heal", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True

def test_v6_gradient_verify_endpoint():
    code = "def linear(x):\n    return 3 * x + 2\n"
    payload = {"code": code, "input_dim": 2, "epsilon": 1e-5}
    res = client.post("/api/v6/gradient-verify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["all_passed"] is True

def test_v6_memory_trace_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json")}
    res = client.post("/api/v6/memory-trace", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "peak_memory_mb" in data

def test_v6_evolutionary_search_endpoint():
    payload = {"base_algorithm": "Transformer", "generations": 2, "population_size": 3}
    res = client.post("/api/v6/evolutionary-search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["candidates"]) >= 1

def test_v6_deconstruct_figure_endpoint():
    payload = {"figure_caption": "Figure 1: Dual-Path Attention block with Feed-Forward network."}
    res = client.post("/api/v6/deconstruct-figure", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) >= 1

def test_v6_normalize_math_endpoint():
    payload = {"latex_str": "\\frac{a}{b} + x^2"}
    res = client.post("/api/v6/normalize-math", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "canonical_sympy" in data

def test_v6_normalize_paper_math_endpoint(sample_project):
    payload = {"paper": sample_project.paper.model_dump(mode="json")}
    res = client.post("/api/v6/normalize-paper-math", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["expressions"]) >= 1

def test_v6_fuse_papers_endpoint(sample_project):
    payload = {
        "paper_a": sample_project.paper.model_dump(mode="json"),
        "paper_b": sample_project.paper.model_dump(mode="json"),
    }
    res = client.post("/api/v6/fuse-papers", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "hybrid_code" in data

def test_v6_leaderboard_endpoint(sample_project):
    payload = {"paper": sample_project.paper.model_dump(mode="json")}
    res = client.post("/api/v6/leaderboard", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "saturation_verdict" in data

def test_v6_poster_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json")}
    res = client.post("/api/v6/poster", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "<!DOCTYPE html>" in data["standalone_poster_html"]

def test_v6_onnx_export_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json"), "opset_version": 17}
    res = client.post("/api/v6/onnx-export", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "onnx_export_script_py" in data

def test_v6_distributed_launcher_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json"), "world_size": 4}
    res = client.post("/api/v6/distributed-launcher", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "ddp_launcher_script_py" in data

def test_v6_semantic_diff_endpoint(sample_project):
    payload = {
        "paper_v1": sample_project.paper.model_dump(mode="json"),
        "paper_v2": sample_project.paper.model_dump(mode="json"),
    }
    res = client.post("/api/v6/semantic-diff", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "diff_items" in data

def test_v6_experiment_matrix_endpoint():
    payload = {
        "matrix_name": "TestSweep",
        "hparam_grid": {"lr": [0.01, 0.001]},
        "seeds": [42]
    }
    res = client.post("/api/v6/experiment-matrix", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_runs"] == 2
