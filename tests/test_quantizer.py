import pytest
import ast
from paperagent.models import PaperProject, ParsedPaper, PaperMetadata
from paperagent.synthesizer.quantizer import PrecisionQuantizer

def create_mock_project(markdown_text: str = "") -> PaperProject:
    return PaperProject(
        id="test-id",
        paper=ParsedPaper(
            metadata=PaperMetadata(title="Test Model"),
            raw_markdown=markdown_text,
            sections=[],
            references=[]
        )
    )

def test_quantizer_memory_reduction():
    quantizer = PrecisionQuantizer()
    # 1 Billion parameters -> 1000M
    project = create_mock_project("This model has 1B parameters.")
    profile = quantizer.profile_quantization(project)

    assert profile.model_name == "Test Model"
    
    # Extract rows for easier testing
    rows = {row.precision: row for row in profile.precision_rows}
    
    # Ensure all precisions are present
    assert "FP32" in rows
    assert "FP16" in rows
    assert "BF16" in rows
    assert "INT8" in rows
    assert "INT4" in rows

    fp32_mem = rows["FP32"].memory_mb
    int4_mem = rows["INT4"].memory_mb
    
    # 1B parameters in FP32 is 4B bytes = 4000 MB
    assert fp32_mem == 4000.0
    
    # INT4 should be exactly 1/8 of FP32 memory
    assert int4_mem == fp32_mem / 8.0

def test_quantizer_recommendation_logic():
    quantizer = PrecisionQuantizer()
    
    # Small model
    p_small = create_mock_project("This model has 100M parameters.")
    prof_small = quantizer.profile_quantization(p_small)
    assert prof_small.recommended_precision == "FP16 / BF16"
    
    # Medium model
    p_medium = create_mock_project("This model has 7B parameters.")
    prof_medium = quantizer.profile_quantization(p_medium)
    assert prof_medium.recommended_precision == "INT8 Weight-Only"
    
    # Large model
    p_large = create_mock_project("This model has 70B parameters.")
    prof_large = quantizer.profile_quantization(p_large)
    assert prof_large.recommended_precision == "INT4 Weight-Only"

def test_quantizer_wrapper_code_syntax():
    quantizer = PrecisionQuantizer()
    project = create_mock_project("No param count here")
    profile = quantizer.profile_quantization(project)
    
    # Verify valid Python code using AST
    try:
        ast.parse(profile.wrapper_code)
    except SyntaxError as e:
        pytest.fail(f"Wrapper code has invalid syntax: {e}")
        
    assert "import torch.ao.quantization" in profile.wrapper_code
    assert "def apply_dynamic_quantization" in profile.wrapper_code