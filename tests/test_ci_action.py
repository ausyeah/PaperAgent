import os
import zipfile
import pytest
from datetime import datetime, timezone
import yaml

from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, SynthesisResult
from paperagent.export.ci_action import generate_github_workflow, export_reproduction_repo_bundle

@pytest.fixture
def mock_paper_project() -> PaperProject:
    metadata = PaperMetadata(
        title="Test Paper",
        authors=["Alice", "Bob"],
        abstract="Test abstract",
        date_published=datetime(2023, 1, 1, tzinfo=timezone.utc),
        arxiv_id="1234.5678"
    )
    paper = ParsedPaper(
        metadata=metadata,
        sections=[],
        raw_markdown="# Test Paper",
        source_type="pdf"
    )
    synthesis = SynthesisResult(
        algorithm_name="Test Algo",
        target_module_code="print('Hello world from algorithm')",
        test_suite_code="def test_algo(): assert True"
    )
    return PaperProject(
        id="test_proj_1",
        paper=paper,
        synthesis=synthesis
    )

def test_generate_github_workflow(mock_paper_project: PaperProject):
    """Test generating a github workflow."""
    yaml_str = generate_github_workflow(mock_paper_project)
    assert isinstance(yaml_str, str)
    assert yaml_str.strip() != ""

    # Check that it's valid YAML
    parsed_yaml = yaml.safe_load(yaml_str)

    assert "on" in parsed_yaml
    assert "push" in parsed_yaml["on"]
    assert "workflow_dispatch" in parsed_yaml["on"]

    assert "jobs" in parsed_yaml
    assert "reproduce" in parsed_yaml["jobs"]
    job = parsed_yaml["jobs"]["reproduce"]

    assert "strategy" in job
    assert "matrix" in job["strategy"]
    assert "python-version" in job["strategy"]["matrix"]
    assert "3.10" in job["strategy"]["matrix"]["python-version"]
    assert "3.11" in job["strategy"]["matrix"]["python-version"]

    assert "steps" in job
    steps = job["steps"]
    step_names = [step.get("name", "") for step in steps]

    assert any("Checkout repository" in name for name in step_names)
    assert any("Set up Python" in name for name in step_names)
    assert any("Install dependencies" in name for name in step_names)
    assert any("Run PyTest Suite" in name for name in step_names)
    assert any("Run Benchmark Script" in name for name in step_names)

def test_export_reproduction_repo_bundle(mock_paper_project: PaperProject, tmp_path):
    """Test exporting reproduction bundle to a zip file."""
    output_zip = os.path.join(tmp_path, "reproduction.zip")

    export_reproduction_repo_bundle(mock_paper_project, output_zip)

    assert os.path.exists(output_zip)

    with zipfile.ZipFile(output_zip, 'r') as zipf:
        file_list = zipf.namelist()

        assert ".github/workflows/reproduce.yml" in file_list
        assert "reproduce.py" in file_list
        assert "test_reproduce.py" in file_list
        assert "requirements.txt" in file_list
        assert "README.md" in file_list

        reproduce_code = zipf.read("reproduce.py").decode("utf-8")
        assert reproduce_code == "print('Hello world from algorithm')"

        test_code = zipf.read("test_reproduce.py").decode("utf-8")
        assert test_code == "def test_algo(): assert True"

        readme_md = zipf.read("README.md").decode("utf-8")
        assert "Reproduction of: Test Paper" in readme_md

def test_export_reproduction_repo_bundle_no_synthesis(mock_paper_project: PaperProject, tmp_path):
    """Test export fails if no synthesis is present."""
    output_zip = os.path.join(tmp_path, "reproduction.zip")
    mock_paper_project.synthesis = None

    with pytest.raises(ValueError, match="PaperProject has no synthesis results"):
        export_reproduction_repo_bundle(mock_paper_project, output_zip)
