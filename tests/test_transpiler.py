import ast
import pytest
from paperagent.models import ParsedPaper, PaperMetadata, MultiFrameworkCode
from paperagent.synthesizer.transpiler import MultiFrameworkTranspiler

def test_transpiler_offline_fallback():
    # Setup mock paper
    paper = ParsedPaper(
        metadata=PaperMetadata(
            title="Test Algorithm Paper",
            authors=["Test Author"],
            abstract="Test Abstract",
            year=2024
        ),
        sections=[]
    )

    # Initialize transpiler (without API keys it should fallback)
    transpiler = MultiFrameworkTranspiler()

    # Run transpiler
    result = transpiler.transpile_all(paper)

    # Verify result type
    assert isinstance(result, MultiFrameworkCode)

    # Verify all frameworks are present
    assert "numpy" in result.implementations
    assert "pytorch" in result.implementations
    assert "jax" in result.implementations

    # Verify ast.parse success on each implementation code
    for fw, impl in result.implementations.items():
        assert impl.framework == fw
        assert impl.verified is True
        # Ensure it actually compiles
        try:
            ast.parse(impl.code)
        except SyntaxError as e:
            pytest.fail(f"SyntaxError in {fw} implementation: {e}")
