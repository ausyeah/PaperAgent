import ast
import pytest
from datetime import datetime, timezone
from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, SynthesisResult
from paperagent.engine.llm_client import LLMClient
from paperagent.synthesizer.kernel import TritonKernelSynthesizer

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

def test_synthesize_triton_kernel_offline():
    project = create_mock_project()
    client = LLMClient()
    # Force empty API keys for mock mode
    client.gemini_api_key = None
    client.openai_api_key = None
    
    synthesizer = TritonKernelSynthesizer(llm_client=client)
    result = synthesizer.synthesize_triton_kernel(project)
    
    assert result.kernel_name == "fused_matmul_kernel"
    assert "2.1x" in result.speedup_vs_eager
    assert "@triton.jit" in result.triton_code
    assert "import torch" in result.benchmark_harness_code
    
    # Check valid AST for both codes
    try:
        ast.parse(result.triton_code)
    except SyntaxError as e:
        pytest.fail(f"triton_code generated invalid Python syntax: {e}")
        
    try:
        ast.parse(result.benchmark_harness_code)
    except SyntaxError as e:
        pytest.fail(f"benchmark_harness_code generated invalid Python syntax: {e}")