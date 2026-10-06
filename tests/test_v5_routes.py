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
    CitationGraph,
    CitationNode,
    PodcastScript,
    PodcastDialogueTurn,
    StoredPaperRecord,
    SynthesisResult,
)

client = TestClient(app)

@pytest.fixture
def sample_project():
    metadata = PaperMetadata(
        title="Scalable Attention and Kernel Synthesis",
        authors=["Alice", "Bob"],
        abstract="We present GPU kernel acceleration for attention mechanisms.",
        arxiv_id="2401.00001",
        year=2024
    )
    formula = ExtractedFormula(
        id="eq-1",
        latex="\\text{Attn}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V",
        plain_explanation="Flash attention kernel formula."
    )
    algo = ExtractedAlgorithm(
        id="algo-1",
        name="Attention Kernel",
        pseudocode="1. Load blocks\n2. Compute attention\n3. Write output",
        inputs=["Q", "K", "V"],
        outputs=["Out"]
    )
    section = PaperSection(
        title="Methodology",
        level=1,
        content="We evaluate on 8 NVIDIA A100 GPUs for 48 hours with learning rate 1e-4 and batch size 64. Code at github.com/test/repo.",
        formulas=[formula],
        algorithms=[algo]
    )
    paper = ParsedPaper(
        metadata=metadata,
        sections=[section],
        raw_markdown="# Scalable Attention and Kernel Synthesis\n| Method | Latency |\n| --- | --- |\n| Eager | 10ms |\n| Triton | 2ms |\n",
        source_type="arxiv"
    )
    synthesis = SynthesisResult(
        algorithm_name="FlashAttention",
        target_module_code="def flash_attention(q, k, v):\n    return q @ k.T @ v\n",
        test_suite_code="def test_flash_attention():\n    assert True\n"
    )
    return PaperProject(
        id="proj-v5",
        paper=paper,
        synthesis=synthesis,
        created_at=datetime.now(timezone.utc)
    )

def test_v5_kernel_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json"), "operation_name": "flash_attention"}
    res = client.post("/api/v5/kernel", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "triton_code" in data
    assert "speedup_vs_eager" in data

def test_v5_committee_endpoint(sample_project):
    payload = {"paper": sample_project.paper.model_dump(mode="json")}
    res = client.post("/api/v5/committee", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["reviews"]) == 3
    assert "final_decision" in data

def test_v5_graph_view_endpoint():
    graph = CitationGraph(
        root_paper_title="Transformer",
        nodes=[
            CitationNode(title="Transformer", authors=["Vaswani et al."]),
            CitationNode(title="Attention RNN", authors=["Bahdanau et al."])
        ],
        edges=[{"source": "Transformer", "target": "Attention RNN", "relation": "builds_on"}]
    )
    payload = {"graph": graph.model_dump(mode="json")}
    res = client.post("/api/v5/graph-view", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "<!DOCTYPE html>" in data["standalone_html"]

def test_v5_dataset_fixture_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json"), "num_samples": 50}
    res = client.post("/api/v5/dataset-fixture", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["num_samples"] == 50
    assert "generator_code" in data

def test_v5_quantize_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json")}
    res = client.post("/api/v5/quantize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["precision_rows"]) >= 4
    assert "recommended_precision" in data

def test_v5_scorecard_endpoint(sample_project):
    payload = {"paper": sample_project.paper.model_dump(mode="json")}
    res = client.post("/api/v5/scorecard", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert "criteria_checklist" in data

def test_v5_extract_tables_endpoint(sample_project):
    payload = {"paper": sample_project.paper.model_dump(mode="json")}
    res = client.post("/api/v5/extract-tables", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "tables" in data

def test_v5_sync_bot_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json"), "target_repo": "test/repo"}
    res = client.post("/api/v5/sync-bot", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "pr_title" in data
    assert len(data["git_commands"]) > 0

def test_v5_derivation_endpoint():
    payload = {
        "formula_from_id": "eq-1",
        "formula_from_latex": "y = x",
        "formula_from_context": "Start",
        "formula_to_id": "eq-2",
        "formula_to_latex": "y + 1 = x + 1",
        "formula_to_context": "Add 1 to both sides"
    }
    res = client.post("/api/v5/derivation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "is_mathematically_sound" in data

def test_v5_tts_ssml_endpoint():
    podcast = PodcastScript(
        episode_title="Test Audio Brief",
        turns=[
            PodcastDialogueTurn(speaker="Host A (Curious)", speech="What is this new method?"),
            PodcastDialogueTurn(speaker="Host B (Expert)", speech="It uses Triton kernels for speed.")
        ]
    )
    payload = {"podcast": podcast.model_dump(mode="json")}
    res = client.post("/api/v5/tts-ssml", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "<speak" in data["ssml_content"]


def test_v5_cluster_endpoint():
    papers = [
        StoredPaperRecord(id="p1", title="Attention Is All You Need", summary="Transformers and attention", created_at="2026-01-01"),
        StoredPaperRecord(id="p2", title="BERT Language Model", summary="Bidirectional Transformers", created_at="2026-01-02"),
        StoredPaperRecord(id="p3", title="LoRA Parameter Efficient", summary="Low-rank adaptation", created_at="2026-01-03"),
    ]
    payload = {"papers": [p.model_dump(mode="json") for p in papers], "k_clusters": 2}
    res = client.post("/api/v5/cluster", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["clusters"]) >= 1

def test_v5_interactive_notebook_endpoint(sample_project):
    payload = {"project": sample_project.model_dump(mode="json")}
    res = client.post("/api/v5/interactive-notebook", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "notebook_json" in data
    assert "ipywidgets" in data["notebook_json"]

def test_v5_benchmark_reproduce_endpoint():
    code = "def run_benchmark(): return {'execution_time_seconds': 0.05, 'throughput_samples_per_sec': 1200.0, 'convergence_metric': {'loss': 1.1}}"
    payload = {"paper_name": "Attention Is All You Need (Transformer)", "code": code}
    res = client.post("/api/v5/benchmark-reproduce", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["reproduction_success"] is True

def test_v5_speedup_endpoint():
    payload = {"algorithm_name": "AttentionKernel", "input_shape": [16, 512, 64]}
    res = client.post("/api/v5/speedup", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "speedup_ratios" in data
    assert "fastest_framework" in data
