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
    AnalysisReport,
    ReviewerCritique,
    SynthesisResult,
)

client = TestClient(app)

@pytest.fixture
def sample_project():
    metadata = PaperMetadata(
        title="Test Attention Mechanisms",
        authors=["Alice", "Bob"],
        abstract="An analysis of attention scaling and state spaces.",
        arxiv_id="2401.00001",
        year=2024
    )
    formula = ExtractedFormula(
        id="eq-1",
        latex="\\text{Attn}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V",
        plain_explanation="Computes weighted values by key similarity."
    )
    algo = ExtractedAlgorithm(
        id="algo-1",
        name="Attention Algorithm",
        pseudocode="1. Matmul Q and K transpose\n2. Scale by sqrt(d)\n3. Softmax and matmul V",
        inputs=["Q", "K", "V"],
        outputs=["Attn"]
    )
    section = PaperSection(
        title="Methodology",
        level=1,
        content="Here we detail the attention mechanism.",
        formulas=[formula],
        algorithms=[algo]
    )
    paper = ParsedPaper(
        metadata=metadata,
        sections=[section],
        raw_markdown="# Test Attention Mechanisms",
        source_type="arxiv"
    )
    critique = ReviewerCritique(
        strengths=["Sound theory", "Clear formulations"],
        weaknesses=["Missing hardware benchmarks"],
        boundary_conditions=["High sequence length"],
        score=7
    )
    analysis = AnalysisReport(
        executive_summary="Explores attention scaling.",
        core_problem="Quadratic compute complexity.",
        key_innovation="Dimension invariant projection.",
        methodology_overview="Matrix factorizations.",
        reviewer_critique=critique
    )
    synthesis = SynthesisResult(
        algorithm_name="ScaledDotProductAttention",
        target_module_code="def attention(q, k, v):\n    return q @ k.T @ v\n",
        test_suite_code="def test_attention():\n    assert True\n"
    )
    return PaperProject(
        id="test-proj-001",
        paper=paper,
        analysis=analysis,
        synthesis=synthesis
    )


def test_v4_ablation_endpoint(sample_project):
    res = client.post("/api/v4/ablation", json=sample_project.model_dump(mode="json"))
    assert res.status_code == 200
    data = res.json()
    assert "variants" in data
    assert len(data["variants"]) >= 1
    assert "ablation_harness_code" in data


def test_v4_survey_endpoint(sample_project):
    res = client.post("/api/v4/survey", json={
        "topic": "Efficient Transformers",
        "papers": [sample_project.paper.model_dump(mode="json")]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["topic"] == "Efficient Transformers"
    assert "taxonomy_tree" in data
    assert "chronology" in data


def test_v4_hardware_endpoint(sample_project):
    res = client.post("/api/v4/hardware", json={
        "project": sample_project.model_dump(mode="json"),
        "param_count_m": 350.0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["parameter_count_million"] == 350.0
    assert "vram_inference_mb" in data
    assert "1k_ctx" in data["vram_inference_mb"]


def test_v4_meta_analysis_endpoint(sample_project):
    res = client.post("/api/v4/meta-analysis", json={
        "topic": "Attention Scaling",
        "projects": [sample_project.model_dump(mode="json"), sample_project.model_dump(mode="json")]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["topic"] == "Attention Scaling"
    assert "claims" in data


def test_v4_environment_endpoint(sample_project):
    res = client.post("/api/v4/environment", json={
        "project": sample_project.model_dump(mode="json"),
        "python_version": "3.11",
        "cuda_version": "12.2"
    })
    assert res.status_code == 200
    data = res.json()
    assert "conda_yaml" in data
    assert "dockerfile_cuda" in data


def test_v4_qa_endpoint(sample_project):
    res = client.post("/api/v4/qa", json={
        "query": "What is the key trick to reduce complexity?",
        "project": sample_project.model_dump(mode="json")
    })
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "citations" in data


def test_v4_podcast_endpoint(sample_project):
    res = client.post("/api/v4/podcast", json=sample_project.model_dump(mode="json"))
    assert res.status_code == 200
    data = res.json()
    assert "turns" in data
    assert len(data["turns"]) >= 1


def test_v4_hf_adapter_endpoint(sample_project):
    res = client.post("/api/v4/hf-adapter", json=sample_project.model_dump(mode="json"))
    assert res.status_code == 200
    data = res.json()
    assert "adapter_module_code" in data
    assert "model_class_name" in data


def test_v4_rebuttal_endpoint(sample_project):
    res = client.post("/api/v4/rebuttal", json={
        "project": sample_project.model_dump(mode="json")
    })
    assert res.status_code == 200
    data = res.json()
    assert "points" in data
    assert "markdown_letter" in data


def test_v4_radar_endpoint():
    res = client.post("/api/v4/radar", json={
        "category_or_query": "cs.CL State Space Models",
        "candidate_papers": [
            {
                "title": "Mamba-2 Architecture",
                "arxiv_id": "2405.00123",
                "summary": "State Space Models for deep learning sequence modeling",
                "score": 0.95
            }
        ],
        "top_k": 3
    })
    assert res.status_code == 200
    data = res.json()
    assert data["category_or_query"] == "cs.CL State Space Models"
    assert len(data["matched_papers"]) >= 1
