import pytest
from unittest.mock import MagicMock
from paperagent.models import FigureSemanticGraph, FigureNode, FigureEdge
from paperagent.engine.llm_client import LLMClient
from paperagent.parser.figure_describer import FigureDeconstructor

def test_deconstruct_figure_llm():
    """Test LLM-based deconstruction with mocked client."""
    mock_client = MagicMock(spec=LLMClient)
    
    mock_graph = FigureSemanticGraph(
        figure_id="fig1",
        caption="A dual-path transformer.",
        nodes=[
            FigureNode(node_id="n1", label="Encoder", node_type="operator"),
            FigureNode(node_id="n2", label="Decoder", node_type="operator")
        ],
        edges=[
            FigureEdge(source_id="n1", target_id="n2", tensor_flow_desc="context")
        ],
        synthesized_code_stub="class DualPath(nn.Module): pass"
    )
    
    mock_client.generate_structured.return_value = mock_graph
    
    deconstructor = FigureDeconstructor(llm_client=mock_client)
    
    caption = "Figure 1: Overview of our Dual-Path Transformer."
    context = "The dual-path architecture processes sequence in parallel."
    
    result = deconstructor.deconstruct_figure(figure_caption=caption, context_text=context)
    
    assert mock_client.generate_structured.called
    assert result.figure_id == "fig1"
    assert len(result.nodes) == 2
    assert len(result.edges) == 1
    assert "class DualPath" in result.synthesized_code_stub

def test_deconstruct_figure_offline_fallback():
    """Test deterministic offline fallback when LLM fails or is missing."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.generate_structured.side_effect = Exception("API Error")
    
    deconstructor = FigureDeconstructor(llm_client=mock_client)
    
    caption = "Figure 1: Our new architecture features an embedding layer, an attention block, and an MLP."
    context = "This feed-forward network uses layernorm."
    
    result = deconstructor.deconstruct_figure(figure_caption=caption, context_text=context)
    
    assert result.figure_id == "fallback-extracted"
    assert len(result.nodes) > 0
    # Should detect 'embedding', 'attention', 'mlp', 'feed-forward', 'layernorm'
    labels = [n.label.lower() for n in result.nodes]
    assert any("embedding" in l for l in labels)
    assert any("attention" in l for l in labels)
    assert any("mlp" in l or "perceptron" in l for l in labels)
    
    assert len(result.edges) == len(result.nodes) - 1
    
    assert "import torch.nn as nn" in result.synthesized_code_stub
    assert "class ExtractedArchitecture(nn.Module):" in result.synthesized_code_stub
    assert "def forward(self, x):" in result.synthesized_code_stub
    
def test_deconstruct_figure_offline_fallback_empty():
    """Test fallback when no keywords are found."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.generate_structured.side_effect = Exception("API Error")
    
    deconstructor = FigureDeconstructor(llm_client=mock_client)
    
    caption = "Figure 1: A very simple model."
    context = "Just some layers."
    
    result = deconstructor.deconstruct_figure(figure_caption=caption, context_text=context)
    
    assert result.figure_id == "fallback-extracted"
    assert len(result.nodes) == 3
    assert len(result.edges) == 2
    
    assert "import torch.nn as nn" in result.synthesized_code_stub
    assert "class Architecture(nn.Module):" in result.synthesized_code_stub
