import pytest
from unittest.mock import MagicMock
from paperagent.models import (
    ParsedPaper, PaperMetadata, PaperSection, ExtractedFormula,
    SynthesisResult, TraceMap
)
from paperagent.engine.code_aligner import CodeMathAligner
from paperagent.engine.llm_client import LLMClient

@pytest.fixture
def dummy_paper():
    metadata = PaperMetadata(
        title="Attention Is All You Need",
        authors=["Vaswani et al."],
        abstract="Transformers.",
        year=2017
    )
    formula1 = ExtractedFormula(
        id="eq-1",
        latex="Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V",
        context_text="The attention mechanism."
    )
    section = PaperSection(
        title="3.2.1 Scaled Dot-Product Attention",
        content="We compute the attention function...",
        formulas=[formula1]
    )
    return ParsedPaper(metadata=metadata, sections=[section])

@pytest.fixture
def dummy_synthesis():
    code = (
        "def scaled_dot_product_attention(Q, K, V):\n"
        "    d_k = Q.size(-1)\n"
        "    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)\n"
        "    p_attn = F.softmax(scores, dim=-1)\n"
        "    return torch.matmul(p_attn, V), p_attn\n"
    )
    return SynthesisResult(
        algorithm_name="Transformer",
        target_module_code=code,
        test_suite_code="def test_attention(): pass"
    )

def test_code_math_aligner_mock_mode(dummy_paper, dummy_synthesis):
    # Use real aligner but let it fail down to mock by simulating LLM error
    # Or rely on the fact that without API keys it will hit the LLM mock or we can force the mock
    mock_llm = MagicMock(spec=LLMClient)
    mock_llm.generate_structured.side_effect = Exception("API Key Missing")

    aligner = CodeMathAligner(llm_client=mock_llm)
    trace_map = aligner.align_code_with_paper(dummy_paper, dummy_synthesis)

    assert isinstance(trace_map, TraceMap)
    assert trace_map.paper_title == dummy_paper.metadata.title
    assert len(trace_map.alignments) == 1

    alignment = trace_map.alignments[0]
    assert alignment.function_name == "compute_loss"  # Hardcoded in mock for now
    assert alignment.target_formula_id == "eq-1"
    assert alignment.target_formula_latex == "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V"
    assert "Mock alignment" in alignment.alignment_notes

def test_code_math_aligner_no_formulas(dummy_paper, dummy_synthesis):
    dummy_paper.sections[0].formulas = []

    aligner = CodeMathAligner()
    trace_map = aligner.align_code_with_paper(dummy_paper, dummy_synthesis)

    assert isinstance(trace_map, TraceMap)
    assert trace_map.paper_title == dummy_paper.metadata.title
    assert len(trace_map.alignments) == 0

def test_code_math_aligner_no_code(dummy_paper, dummy_synthesis):
    dummy_synthesis.target_module_code = ""

    aligner = CodeMathAligner()
    trace_map = aligner.align_code_with_paper(dummy_paper, dummy_synthesis)

    assert isinstance(trace_map, TraceMap)
    assert trace_map.paper_title == dummy_paper.metadata.title
    assert len(trace_map.alignments) == 0
