import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from paperagent.models import (
    PaperProject,
    ParsedPaper,
    PaperMetadata,
    AnalysisReport,
    SynthesisResult,
    ReviewerCritique
)
from paperagent.storage.db import PaperStorage

@pytest.fixture
def temp_db_path(tmp_path):
    return tmp_path / "test_library.db"

@pytest.fixture
def storage(temp_db_path):
    return PaperStorage(db_path=temp_db_path)

@pytest.fixture
def sample_project():
    metadata = PaperMetadata(
        title="Attention Is All You Need",
        arxiv_id="1706.03762"
    )
    paper = ParsedPaper(metadata=metadata)

    critique = ReviewerCritique(
        strengths=["Great"],
        weaknesses=["None"],
        boundary_conditions=["None"],
        potential_reproducibility_pitfalls=["None"],
        score=10
    )

    analysis = AnalysisReport(
        executive_summary="Transformers beat RNNs.",
        core_problem="Sequence modeling",
        key_innovation="Self-attention",
        methodology_overview="Stacked encoder-decoder",
        reviewer_critique=critique
    )

    synthesis = SynthesisResult(
        algorithm_name="Multi-Head Attention",
        target_module_code="def attention(): pass",
        test_suite_code="def test_attention(): pass"
    )

    return PaperProject(
        id="test_proj_1",
        created_at=datetime.now(timezone.utc),
        paper=paper,
        analysis=analysis,
        synthesis=synthesis
    )

def test_initialization(temp_db_path):
    storage = PaperStorage(db_path=temp_db_path)
    assert temp_db_path.exists()

    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
        assert cursor.fetchone() is not None

def test_save_and_get_paper(storage, sample_project):
    record = storage.save_paper(sample_project, tags=["nlp", "transformer"])

    assert record.id == "test_proj_1"
    assert record.title == "Attention Is All You Need"
    assert record.arxiv_id == "1706.03762"
    assert record.has_code is True
    assert record.tags == ["nlp", "transformer"]
    assert record.summary == "Transformers beat RNNs."

    fetched = storage.get_paper("test_proj_1")
    assert fetched is not None
    assert fetched.id == "test_proj_1"
    assert fetched.paper.metadata.title == "Attention Is All You Need"
    assert fetched.analysis.executive_summary == "Transformers beat RNNs."
    assert fetched.synthesis.algorithm_name == "Multi-Head Attention"

def test_get_paper_not_found(storage):
    assert storage.get_paper("non_existent_id") is None

def test_list_papers(storage, sample_project):
    # Save a couple of projects
    storage.save_paper(sample_project, tags=["nlp"])

    sample_project.id = "test_proj_2"
    sample_project.paper.metadata.title = "BERT"
    sample_project.paper.metadata.arxiv_id = "1810.04805"
    storage.save_paper(sample_project, tags=["nlp", "bert"])

    records = storage.list_papers()
    assert len(records) == 2

    nlp_records = storage.list_papers(tag="nlp")
    assert len(nlp_records) == 2

    bert_records = storage.list_papers(tag="bert")
    assert len(bert_records) == 1
    assert bert_records[0].id == "test_proj_2"

def test_search_papers(storage, sample_project):
    storage.save_paper(sample_project)

    sample_project.id = "test_proj_2"
    sample_project.paper.metadata.title = "BERT"
    sample_project.paper.metadata.arxiv_id = "1810.04805"
    sample_project.analysis.executive_summary = "Bidirectional Encoder Representations"
    storage.save_paper(sample_project)

    results = storage.search_papers("Attention")
    assert len(results) == 1
    assert results[0].id == "test_proj_1"

    results = storage.search_papers("Bidirectional")
    assert len(results) == 1
    assert results[0].id == "test_proj_2"

    results = storage.search_papers("1706.03762")
    assert len(results) == 1
    assert results[0].id == "test_proj_1"

def test_delete_paper(storage, sample_project):
    storage.save_paper(sample_project)
    assert storage.get_paper("test_proj_1") is not None

    assert storage.delete_paper("test_proj_1") is True
    assert storage.get_paper("test_proj_1") is None

    assert storage.delete_paper("non_existent_id") is False
