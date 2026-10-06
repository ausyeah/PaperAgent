from fastapi.testclient import TestClient
from paperagent.web.app import app

client = TestClient(app)

mock_parsed_paper = {
    "metadata": {
        "title": "Mock Title",
        "authors": ["Alice", "Bob"],
        "abstract": "Abstract",
        "arxiv_id": "1234.5678"
    },
    "sections": [],
    "raw_markdown": "",
    "source_type": "pdf"
}

mock_extracted_formula = {
    "id": "eq-1",
    "latex": "E = mc^2",
    "context": "Context",
    "section_id": "sec-1"
}

mock_synthesis_result = {
    "algorithm_name": "Test Algo",
    "target_module_code": "def func(): pass",
    "test_suite_code": "def test_func(): pass",
    "toy_benchmark_code": "print('done')",
    "execution_result": None,
    "jupyter_notebook_json": None
}

mock_paper_project = {
    "id": "proj-123",
    "created_at": "2023-01-01T00:00:00Z",
    "paper": mock_parsed_paper,
    "analysis": None,
    "synthesis": None
}

def test_citation_graph_endpoint():
    response = client.post("/api/v3/citation-graph", json=mock_parsed_paper)
    assert response.status_code == 200
    data = response.json()
    assert "root_paper_title" in data
    assert data["root_paper_title"] == "Mock Title"
    assert "nodes" in data
    assert "edges" in data

def test_verify_formula_endpoint():
    response = client.post("/api/v3/formula/verify", json=mock_extracted_formula)
    assert response.status_code == 200
    data = response.json()
    assert "formula_id" in data
    assert data["formula_id"] == "eq-1"
    assert data["invariants_passed"] is True

def test_transpile_code_endpoint():
    response = client.post("/api/v3/code/transpile", json=mock_parsed_paper)
    assert response.status_code == 200
    data = response.json()
    assert "paper_title" in data
    assert data["paper_title"] == "Mock Title"
    assert "implementations" in data

def test_align_code_endpoint():
    payload = {
        "paper": mock_parsed_paper,
        "synthesis": mock_synthesis_result
    }
    response = client.post("/api/v3/code/align", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "paper_title" in data
    assert data["paper_title"] == "Mock Title"
    assert "alignments" in data

def test_export_slides_endpoint():
    response = client.post("/api/v3/export/slides", json=mock_paper_project)
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "Slides for Mock Title" in data["title"]
    assert "marp_markdown" in data

def test_download_slides_endpoint():
    response = client.get("/api/v3/export/slides/download", params={"paper_id": "test1234"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/markdown; charset=utf-8"
    assert "slides_test1234.md" in response.headers["content-disposition"]
    assert "marp: true" in response.text
