import pytest
from fastapi.testclient import TestClient
import json
import os
from paperagent.web.app import app

# Use in-memory DB for tests via env var
os.environ["PAPERAGENT_DB_PATH"] = "file::memory:?cache=shared"

client = TestClient(app)

def test_library_crud():
    # 1. Get empty library
    resp = client.get("/api/library")
    assert resp.status_code == 200
    assert resp.json() == []

    # 2. Add a paper
    dummy_project = {
        "id": "proj_123",
        "created_at": "2024-01-01T00:00:00Z",
        "paper": {
            "metadata": {
                "title": "Test Paper",
                "authors": ["Test Author"],
                "abstract": "Test abstract"
            },
            "sections": [],
            "raw_markdown": "Test markdown",
            "source_type": "pdf"
        }
    }

    resp = client.post("/api/library", json=dummy_project)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "proj_123"
    assert data["title"] == "Test Paper"

    # 3. Get the list again
    resp = client.get("/api/library")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # 4. Get specific paper
    resp = client.get("/api/library/proj_123")
    assert resp.status_code == 200
    assert resp.json()["id"] == "proj_123"

    # 5. Delete specific paper
    resp = client.delete("/api/library/proj_123")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"

    # 6. Verify deleted
    resp = client.get("/api/library/proj_123")
    assert resp.status_code == 404

def test_compare_endpoint():
    dummy_paper_a = {
        "metadata": {"title": "Paper A", "authors": ["A"]},
        "sections": [],
        "raw_markdown": "",
        "source_type": "pdf"
    }
    dummy_paper_b = {
        "metadata": {"title": "Paper B", "authors": ["B"]},
        "sections": [],
        "raw_markdown": "",
        "source_type": "pdf"
    }
    resp = client.post("/api/compare", json={"paper_a": dummy_paper_a, "paper_b": dummy_paper_b})
    assert resp.status_code == 200
    data = resp.json()
    assert data["paper_a_title"] == "Paper A"
    assert data["paper_b_title"] == "Paper B"
    assert "dimensions" in data

def test_openreview_endpoint():
    dummy_paper = {
        "metadata": {"title": "Test OpenReview Paper", "authors": ["A"]},
        "sections": [],
        "raw_markdown": "",
        "source_type": "pdf"
    }
    resp = client.post("/api/openreview", json=dummy_paper)
    assert resp.status_code == 200
    data = resp.json()
    assert data["paper_title"] == "Test OpenReview Paper"
    assert "summary_of_work" in data
    assert "soundness_score" in data

def test_export_latex():
    # Setup dummy project in memory DB
    dummy_project = {
        "id": "proj_export",
        "created_at": "2024-01-01T00:00:00Z",
        "paper": {
            "metadata": {
                "title": "Export Test",
                "authors": ["Test Author"]
            },
            "sections": [],
            "raw_markdown": "Test markdown",
            "source_type": "pdf"
        }
    }
    client.post("/api/library", json=dummy_project)

    resp = client.get("/api/paper/export/latex?paper_id=proj_export")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"

    # Clean up
    client.delete("/api/library/proj_export")
