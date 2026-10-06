import ast
import pytest
from datetime import datetime, timezone
from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, SynthesisResult
from paperagent.engine.llm_client import LLMClient
from paperagent.synthesizer.hf_adapter import synthesize_hf_adapter

def create_mock_project() -> PaperProject:
    metadata = PaperMetadata(
        title="Test Paper",
        authors=["Author 1"],
        abstract="Test abstract",
        year=2024,
        url="http://test.com",
        doi="10.1000/xyz123"
    )
    paper = ParsedPaper(
        id="test-id",
        metadata=metadata,
        sections=[]
    )
    synthesis = SynthesisResult(
        algorithm_name="TestAlgo",
        target_module_code="import torch\nclass TestAlgo(torch.nn.Module):\n    def forward(self, x):\n        return x",
        test_suite_code="def test_algo():\n    pass"
    )
    return PaperProject(
        id="project-id",
        created_at=datetime.now(timezone.utc),
        paper=paper,
        synthesis=synthesis
    )

def test_offline_fallback():
    project = create_mock_project()
    client = LLMClient()
    # Force empty API keys for mock mode
    client.gemini_api_key = None
    client.openai_api_key = None
    
    result = synthesize_hf_adapter(project, client)
    
    assert result.model_class_name == "SynthesizedModel"
    assert result.config_class_name == "SynthesizedConfig"
    assert "class SynthesizedConfig(PretrainedConfig):" in result.adapter_module_code
    assert "class SynthesizedModel(PreTrainedModel):" in result.adapter_module_code
    assert "from_pretrained" in result.example_usage_code
    
    # Check valid AST
    try:
        ast.parse(result.adapter_module_code)
    except SyntaxError as e:
        pytest.fail(f"adapter_module_code generated invalid Python syntax: {e}")
        
    try:
        ast.parse(result.example_usage_code)
    except SyntaxError as e:
        pytest.fail(f"example_usage_code generated invalid Python syntax: {e}")

def test_synthesize_hf_adapter_no_synthesis():
    project = create_mock_project()
    project.synthesis = None
    with pytest.raises(ValueError, match="PaperProject must have a synthesis result"):
        synthesize_hf_adapter(project)
