import os
import json
import pytest
from paperagent.models import CitationGraph, CitationNode, GraphVisualizationBundle
from paperagent.export.graph_view import export_citation_graph_html, ROLE_COLORS

@pytest.fixture
def sample_graph():
    return CitationGraph(
        root_paper_title="Root Paper: An Overview",
        nodes=[
            CitationNode(title="Root Paper: An Overview", influence_role="related", authors=["Alice", "Bob"]),
            CitationNode(title="Foundation Model Alpha", influence_role="foundation", authors=["Charlie"]),
            CitationNode(title="Baseline Net", influence_role="baseline"),
            CitationNode(title="Successor Transformer", influence_role="successor"),
            CitationNode(title="Related Study", influence_role="related"),
        ],
        edges=[
            {"source": "Root Paper: An Overview", "target": "Foundation Model Alpha", "relation": "builds on"},
            {"source": "Root Paper: An Overview", "target": "Baseline Net", "relation": "compares with"},
            {"source": "Successor Transformer", "target": "Root Paper: An Overview", "relation": "improves"},
            {"source": "Root Paper: An Overview", "target": "Related Study", "relation": "mentions"},
        ],
        lineage_summary="A summary."
    )

def test_export_citation_graph_html_returns_bundle(sample_graph):
    bundle = export_citation_graph_html(sample_graph)
    
    assert isinstance(bundle, GraphVisualizationBundle)
    assert bundle.paper_title == "Root Paper: An Overview"
    assert len(bundle.nodes) == 5
    assert len(bundle.edges) == 4
    
    # Check node mapping
    root_node = next(n for n in bundle.nodes if n["id"] == "Root Paper: An Overview")
    assert root_node["color"] == ROLE_COLORS["related"]
    assert "Alice" in root_node["title"]
    
    foundation_node = next(n for n in bundle.nodes if n["id"] == "Foundation Model Alpha")
    assert foundation_node["color"] == ROLE_COLORS["foundation"]
    
    baseline_node = next(n for n in bundle.nodes if n["id"] == "Baseline Net")
    assert baseline_node["color"] == ROLE_COLORS["baseline"]

    successor_node = next(n for n in bundle.nodes if n["id"] == "Successor Transformer")
    assert successor_node["color"] == ROLE_COLORS["successor"]
    
    # Check edge mapping
    assert any(e["from"] == "Root Paper: An Overview" and e["to"] == "Foundation Model Alpha" for e in bundle.edges)

def test_export_citation_graph_html_content(sample_graph):
    bundle = export_citation_graph_html(sample_graph)
    
    html = bundle.standalone_html
    assert "vis-network.min.js" in html
    assert "Citation Graph: Root Paper: An Overview" in html
    assert "forceAtlas2Based" in html
    
    # Check that nodes and edges data is embedded correctly
    assert json.dumps(bundle.nodes) in html
    assert json.dumps(bundle.edges) in html
    
    # Check for search elements
    assert "id=\"search\"" in html
    
def test_export_citation_graph_html_to_file(sample_graph, tmp_path):
    output_path = tmp_path / "graph.html"
    bundle = export_citation_graph_html(sample_graph, output_path=str(output_path))
    
    assert output_path.exists()
    
    content = output_path.read_text(encoding="utf-8")
    assert content == bundle.standalone_html