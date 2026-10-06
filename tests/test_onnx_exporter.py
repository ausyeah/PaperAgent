import ast
from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, ONNXExportBundle
from paperagent.export.onnx_exporter import ONNXExportGenerator


def test_onnx_export_generator():
    """Test generating ONNX and TensorRT scripts."""
    
    # Create a mock paper project
    project = PaperProject(
        id="test-model-123",
        paper=ParsedPaper(
            metadata=PaperMetadata(
                title="Test Paper", 
                authors=["Alice", "Bob"], 
                year=2024, 
                url="https://arxiv.org/abs/2401.00000", 
                abstract="A test abstract"
            )
        )
    )
    
    # Instantiate the generator
    generator = ONNXExportGenerator()
    
    # Generate the bundle
    bundle = generator.generate_export_bundle(project, opset_version=17)
    
    # Verify return type and fields
    assert isinstance(bundle, ONNXExportBundle)
    assert bundle.model_name == "test_model_123"
    assert bundle.opset_version == 17
    assert "onnxsim" in bundle.simplification_instructions
    
    # Validate Python syntax of the generated scripts
    try:
        ast.parse(bundle.onnx_export_script_py)
    except SyntaxError as e:
        assert False, f"ONNX export script is not valid Python: {e}"
        
    try:
        ast.parse(bundle.tensorrt_builder_script_py)
    except SyntaxError as e:
        assert False, f"TensorRT builder script is not valid Python: {e}"
        
    # Check for specific expected content in scripts
    assert "torch.onnx.export" in bundle.onnx_export_script_py
    assert "dynamic_axes" in bundle.onnx_export_script_py
    assert "tensorrt as trt" in bundle.tensorrt_builder_script_py
    assert "trt.BuilderFlag.FP16" in bundle.tensorrt_builder_script_py
    assert "trt.BuilderFlag.INT8" in bundle.tensorrt_builder_script_py