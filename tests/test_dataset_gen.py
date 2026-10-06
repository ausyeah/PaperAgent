import ast
import textwrap
from datetime import datetime, timezone
import pytest

from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, SyntheticDatasetFixture
from paperagent.synthesizer.dataset_gen import SyntheticDatasetGenerator

def test_dataset_generator():
    generator = SyntheticDatasetGenerator()

    # Create dummy project
    metadata = PaperMetadata(
        title="Test Paper",
        authors=["Alice", "Bob"]
    )
    paper = ParsedPaper(metadata=metadata)
    project = PaperProject(id="testproject", paper=paper)

    # Generate fixture
    fixture = generator.generate_dataset_fixture(project, num_samples=100)

    # Verify fixture structure
    assert isinstance(fixture, SyntheticDatasetFixture)
    assert fixture.dataset_name == "SyntheticTestprojectDataset"
    assert fixture.num_samples == 100
    assert "Input Shape: [batch_size, 128, 256]" in fixture.sample_batch_summary

    # 1. AST parsing verification
    try:
        ast.parse(fixture.generator_code)
    except SyntaxError as e:
        pytest.fail(f"Generated code has invalid syntax: {e}")

    # 2. Execution and shape matching via exec (if torch is installed)
    try:
        import torch
    except ImportError:
        # torch is not installed in the current environment; AST check passed
        return

    local_vars = {}
    try:
        exec(fixture.generator_code, globals(), local_vars)
    except Exception as e:
        pytest.fail(f"Generated code failed to execute: {e}")

    dataset_class = local_vars.get("SyntheticTestprojectDataset")
    assert dataset_class is not None, "Dataset class not found in generated code namespace."
    
    get_dataloader = local_vars.get("get_dataloader")
    assert callable(get_dataloader), "get_dataloader function not found or not callable."

    # Test get_dataloader
    dataloader = get_dataloader(batch_size=8)
    batch = next(iter(dataloader))
    
    inputs, targets = batch
    
    # Check shapes
    assert inputs.shape == (8, 128, 256)
    assert targets.shape == (8,)

