import pytest
import ast
import asyncio
from paperagent.models import ParsedPaper, PaperMetadata
from paperagent.engine.multi_paper_synthesizer import CrossPaperFusionSynthesizer

def create_mock_paper(title: str) -> ParsedPaper:
    metadata = PaperMetadata(title=title)
    return ParsedPaper(metadata=metadata, sections=[])

def test_cross_paper_fusion_offline_fallback():
    synthesizer = CrossPaperFusionSynthesizer()
    paper_a = create_mock_paper("Mamba: Linear-Time Sequence Modeling")
    paper_b = create_mock_paper("Attention Is All You Need")

    # Sync invocation (which uses fallback since mock LLMClient isn't passed and true client fails/returns dummy)
    # Actually, LLMClient by default in tests might try to hit API or return mock.
    # We can pass an LLMClient configured to fail, or just rely on the fallback logic inside _get_fallback_result.
    # To strictly test the fallback, let's call it directly first.
    result = synthesizer._get_fallback_result(paper_a, paper_b)
    
    assert result is not None
    assert result.source_paper_a == "Mamba: Linear-Time Sequence Modeling"
    assert result.source_paper_b == "Attention Is All You Need"
    assert "Hybrid_Mamba_Attention" in result.hybrid_algorithm_name
    
    # Verify Python syntax
    try:
        ast.parse(result.hybrid_code)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in synthesized hybrid_code: {e}")
        
    try:
        ast.parse(result.test_suite_code)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in synthesized test_suite_code: {e}")

@pytest.mark.asyncio
async def test_cross_paper_fusion_async_fallback(monkeypatch):
    from paperagent.engine.llm_client import LLMClient
    synthesizer = CrossPaperFusionSynthesizer()
    paper_a = create_mock_paper("Mamba: Linear-Time Sequence Modeling")
    paper_b = create_mock_paper("Attention Is All You Need")

    # Force LLMClient to fail so we hit the exception fallback path
    async def mock_generate_structured_async(*args, **kwargs):
        raise ValueError("Simulated API failure")
    monkeypatch.setattr(LLMClient, "generate_structured_async", mock_generate_structured_async)

    # In a testing environment without valid keys, this should hit the exception and return the fallback.
    result = await synthesizer.fuse_papers_async(paper_a, paper_b)
    
    assert result is not None
    assert result.source_paper_a == "Mamba: Linear-Time Sequence Modeling"
    assert result.source_paper_b == "Attention Is All You Need"
    assert "Hybrid_Mamba_Attention" in result.hybrid_algorithm_name