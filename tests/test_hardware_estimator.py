import pytest
from paperagent.models import PaperProject, ParsedPaper, PaperMetadata
from paperagent.synthesizer.hardware_estimator import HardwareEstimator

@pytest.fixture
def sample_project():
    metadata = PaperMetadata(title="Transformer", authors=["Vaswani"], abstract="Attention is all you need.")
    paper = ParsedPaper(metadata=metadata, raw_markdown="We trained a model with 7B parameters.")
    return PaperProject(id="123", paper=paper)

def test_estimate_hardware_profile(sample_project):
    estimator = HardwareEstimator()
    profile = estimator.estimate_hardware_profile(sample_project)
    
    assert profile.model_name == "Transformer"
    assert profile.parameter_count_million == 7000.0
    
    assert "1k_ctx" in profile.vram_inference_mb
    assert profile.vram_inference_mb["1k_ctx"] > 0
    assert "128k_ctx" in profile.vram_inference_mb
    assert profile.vram_inference_mb["128k_ctx"] > profile.vram_inference_mb["1k_ctx"]

    assert "standard_mixed_precision_MB" in profile.vram_training_mb
    assert profile.vram_training_mb["standard_mixed_precision_MB"] > 0

    assert "NVIDIA" in profile.recommended_gpu or "Cluster" in profile.recommended_gpu

    assert "import optuna" in profile.optuna_hparam_search_code
    assert "def objective(trial):" in profile.optuna_hparam_search_code

def test_infer_param_count_from_text():
    estimator = HardwareEstimator()
    assert estimator._infer_param_count_from_text("Model has 110M params") == 110.0
    assert estimator._infer_param_count_from_text("Model has 7.5B parameters") == 7500.0
    assert estimator._infer_param_count_from_text("No params here") is None

def test_gpu_recommendation():
    estimator = HardwareEstimator()
    assert estimator._recommend_gpu(10 * 1024) == "NVIDIA RTX 4070 (12GB) / RTX 3060"
    assert estimator._recommend_gpu(20 * 1024) == "NVIDIA RTX 4090 (24GB) / RTX 3090"
    assert estimator._recommend_gpu(30 * 1024) == "NVIDIA A100 (40GB)"
    assert estimator._recommend_gpu(60 * 1024) == "NVIDIA A100 (80GB) / H100 (80GB)"
    assert estimator._recommend_gpu(100 * 1024) == "Multi-H100 Cluster"