import os
import tempfile
import pytest
from pathlib import Path
from datetime import datetime, timezone

from paperagent.models import (
    PaperProject, ParsedPaper, PaperMetadata, PaperSection,
    AnalysisReport, SynthesisResult
)
from paperagent.export.environment import generate_environment_bundle, export_environment_bundle


@pytest.fixture
def mock_project():
    meta = PaperMetadata(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        abstract="We propose a new simple network architecture, the Transformer.",
        year=2017,
        arxiv_id="1706.03762"
    )

    paper = ParsedPaper(metadata=meta, sections=[], source_type="arxiv")

    synthesis = SynthesisResult(
        algorithm_name="Scaled Dot-Product Attention",
        target_module_code="import torch\nimport numpy as np\nfrom sklearn import metrics\n\ndef attention(q, k, v):\n    pass",
        test_suite_code="import scipy\nimport cv2\ndef test_attention():\n    assert True",
        toy_benchmark_code="import pandas as pd\nif __name__ == '__main__':\n    print('Run')"
    )

    return PaperProject(
        id="proj-env",
        paper=paper,
        synthesis=synthesis
    )


def test_generate_environment_bundle(mock_project):
    bundle = generate_environment_bundle(mock_project, python_version="3.11", cuda_version="11.8")
    
    assert bundle.paper_title == "Attention Is All You Need"
    
    # check conda_yaml
    assert "name: attention_is_all_you_need" in bundle.conda_yaml
    assert "- python=3.11" in bundle.conda_yaml
    assert "- torch" in bundle.conda_yaml
    assert "- numpy" in bundle.conda_yaml
    assert "- scikit-learn" in bundle.conda_yaml
    assert "- scipy" in bundle.conda_yaml
    assert "- opencv-python" in bundle.conda_yaml
    assert "- pandas" in bundle.conda_yaml
    assert "- pytest" in bundle.conda_yaml  # Added automatically for test suite

    # check dockerfile_cuda
    assert "FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04" in bundle.dockerfile_cuda
    assert "COPY requirements.txt ." in bundle.dockerfile_cuda
    assert "RUN pip install --no-cache-dir -r requirements.txt" in bundle.dockerfile_cuda

    # check requirements_txt
    reqs = bundle.requirements_txt.splitlines()
    # Check that base library names exist in the requirements (some may be pinned)
    reqs_str = bundle.requirements_txt
    assert "torch" in reqs_str
    assert "numpy" in reqs_str
    assert "scikit-learn" in reqs_str
    assert "scipy" in reqs_str
    assert "opencv-python" in reqs_str
    assert "pandas" in reqs_str
    assert "pytest" in reqs_str

    # check scripts
    assert "python -m pytest test_reproduce.py -v" in bundle.reproduction_script_sh
    assert "python reproduce.py" in bundle.reproduction_script_sh
    assert "python -m pytest test_reproduce.py -v" in bundle.reproduction_script_ps1
    assert "python reproduce.py" in bundle.reproduction_script_ps1


def test_export_environment_bundle(mock_project):
    with tempfile.TemporaryDirectory() as temp_dir:
        out_path = export_environment_bundle(mock_project, temp_dir)
        
        assert os.path.exists(out_path)
        assert os.path.isdir(out_path)
        
        files = os.listdir(out_path)
        assert "environment.yml" in files
        assert "Dockerfile" in files
        assert "requirements.txt" in files
        assert "reproduce.sh" in files
        assert "reproduce.ps1" in files
        
        # Check permissions for reproduce.sh (POSIX systems)
        if os.name != "nt":
            sh_stat = os.stat(os.path.join(out_path, "reproduce.sh"))
            assert sh_stat.st_mode & 0o111
        
        # Check file content basic sanity
        with open(os.path.join(out_path, "requirements.txt"), "r") as f:
            content = f.read()
            assert "torch" in content
            assert "numpy" in content