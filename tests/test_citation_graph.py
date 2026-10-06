import pytest
from paperagent.models import ParsedPaper, PaperMetadata, PaperSection, CitationGraph, CitationNode
from paperagent.parser.citation_graph import CitationGraphBuilder
from paperagent.engine.llm_client import LLMClient

def test_citation_graph_builder_mock():
    paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper", authors=["A. Author"]),
        sections=[
            PaperSection(title="References", text="[1] Foundational Paper, Author B, 2020.", level=1)
        ],
        raw_markdown="References\n[1] Foundational Paper, Author B, 2020."
    )

    # Empty LLMClient to force fallback
    client = LLMClient()
    client.gemini_api_key = None
    client.openai_api_key = None

    builder = CitationGraphBuilder(llm_client=client)
    graph = builder.build_citation_graph(paper)

    assert isinstance(graph, CitationGraph)
    assert graph.root_paper_title == "Test Paper"
    assert len(graph.nodes) == 4

    roles = [node.influence_role for node in graph.nodes]
    assert "foundation" in roles
    assert "baseline" in roles
    assert "successor" in roles
    assert "related" in roles

    assert len(graph.edges) == 4
    assert graph.lineage_summary != ""

@pytest.mark.asyncio
async def test_citation_graph_builder_async_mock():
    paper = ParsedPaper(
        metadata=PaperMetadata(title="Async Test Paper", authors=["C. Author"]),
        sections=[],
        raw_markdown="References\n[1] Another Paper, Author D, 2021."
    )

    client = LLMClient()
    client.gemini_api_key = None
    client.openai_api_key = None

    builder = CitationGraphBuilder(llm_client=client)
    graph = await builder.build_citation_graph_async(paper)

    assert isinstance(graph, CitationGraph)
    assert graph.root_paper_title == "Async Test Paper"
    assert len(graph.nodes) > 0
