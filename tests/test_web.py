import pytest
from fastapi.testclient import TestClient
import json

from paperagent.web.app import app

client = TestClient(app)

def test_parse_endpoint():
    response = client.post("/api/paper/parse", data={"source": "arxiv:2312.12456"})
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert data["metadata"]["arxiv_id"] == "arxiv:2312.12456"
    assert len(data["sections"]) == 2

def test_analyze_endpoint():
    # Provide dummy ParsedPaper data
    dummy_paper = {
        "metadata": {
            "title": "Test",
            "authors": ["Test Author"],
            "abstract": "Test abstract"
        },
        "sections": [],
        "raw_markdown": "Test markdown",
        "source_type": "pdf"
    }
    response = client.post("/api/paper/analyze", json=dummy_paper)
    assert response.status_code == 200
    data = response.json()
    assert "executive_summary" in data
    assert "reviewer_critique" in data
    assert data["reviewer_critique"]["score"] == 7

def test_synthesize_endpoint():
    dummy_paper = {
        "metadata": {
            "title": "Test",
            "authors": ["Test Author"],
            "abstract": "Test abstract"
        },
        "sections": [],
        "raw_markdown": "Test markdown",
        "source_type": "pdf"
    }
    response = client.post("/api/paper/synthesize", json=dummy_paper)
    assert response.status_code == 200
    data = response.json()
    assert "target_module_code" in data
    assert "test_suite_code" in data

def test_execute_endpoint():
    code = "print('Hello World')\n"
    response = client.post("/api/paper/execute", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Hello World" in data["stdout"]

def test_export_markdown():
    response = client.get("/api/paper/export/markdown")
    assert response.status_code == 200
    assert response.text.startswith("# Exported Paper")

def test_export_notebook():
    response = client.get("/api/paper/export/notebook")
    assert response.status_code == 200
    data = response.json()
    assert "cells" in data
    assert data["nbformat"] == 4
