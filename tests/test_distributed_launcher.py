import pytest
import ast
import yaml
from datetime import datetime, timezone

from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, SynthesisResult
from paperagent.synthesizer.distributed_launcher import DistributedLaunchGenerator

@pytest.fixture
def dummy_project():
    metadata = PaperMetadata(
        title="Test Paper",
        authors=["Alice", "Bob"],
        abstract="Test Abstract",
        published_date=datetime.now(timezone.utc),
        source_url="http://example.com/test.pdf"
    )
    paper = ParsedPaper(metadata=metadata)
    
    synthesis = SynthesisResult(
        algorithm_name="TestAlgo",
        target_module_code="""
import torch
import torch.nn as nn
class TestAlgo(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 10)
    def forward(self, x):
        return self.fc(x)
""",
        test_suite_code="def test_algo(): pass"
    )
    
    return PaperProject(id="test_proj", paper=paper, synthesis=synthesis)

def test_generate_distributed_bundle_offline(dummy_project):
    generator = DistributedLaunchGenerator()
    
    # We don't set API keys, so it should fallback
    bundle = generator.generate_distributed_bundle(dummy_project, world_size=4)
    
    assert bundle is not None
    assert bundle.recommended_world_size == 4
    assert bundle.model_name == "SynthesizedDistributedModel"
    
    # Verify Python AST
    try:
        ast.parse(bundle.ddp_launcher_script_py)
    except SyntaxError as e:
        pytest.fail(f"Generated DDP script has invalid Python syntax: {e}")
        
    # Verify YAML config
    try:
        yaml_content = yaml.safe_load(bundle.fsdp_config_yaml)
        assert isinstance(yaml_content, dict)
        assert "fsdp_config" in yaml_content
    except yaml.YAMLError as e:
        pytest.fail(f"Generated FSDP config has invalid YAML syntax: {e}")
        
    # Verify Slurm script
    assert "#SBATCH --job-name=" in bundle.slurm_batch_script_sh
    assert "srun torchrun" in bundle.slurm_batch_script_sh
