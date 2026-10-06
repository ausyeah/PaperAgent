import pytest
import datetime
from paperagent.storage.radar import ArxivRadar
from paperagent.storage.vector_index import PaperSearchIndex
from paperagent.models import StoredPaperRecord

def test_empty_candidates():
    radar = ArxivRadar()
    report = radar.generate_daily_digest(
        category_or_query="machine learning",
        candidate_papers=[],
        top_k=5
    )
    assert report.category_or_query == "machine learning"
    assert len(report.matched_papers) == 0
    assert "No new papers found" in report.executive_briefing


def test_keyword_ranking():
    radar = ArxivRadar()
    candidates = [
        {"id": "1", "title": "Understanding large language models", "summary": "We train LLMs..."},
        {"id": "2", "title": "A new method for graph neural networks", "summary": "GNNs are cool..."},
        {"id": "3", "title": "Language models are few shot learners", "summary": "GPT-3 is huge..."},
    ]
    report = radar.generate_daily_digest(
        category_or_query="language models",
        candidate_papers=candidates,
        top_k=2
    )
    
    assert report.category_or_query == "language models"
    assert len(report.matched_papers) <= 2
    assert len(report.matched_papers) > 0
    
    titles = [p["title"] for p in report.matched_papers]
    assert any("language model" in t.lower() for t in titles)
    assert "identified" in report.executive_briefing
    assert "highly relevant breakthroughs" in report.executive_briefing


def test_watchlist_ranking():
    # Setup a global watchlist index
    watchlist = PaperSearchIndex()
    watchlist.add_paper(StoredPaperRecord(
        id="w1", 
        title="Reinforcement Learning from Human Feedback", 
        summary="RLHF is important for alignment.",
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    ))
    
    radar = ArxivRadar(vector_index=watchlist)
    
    candidates = [
        {"id": "c1", "title": "Generative adversarial networks", "summary": "GANs"},
        {"id": "c2", "title": "New alignment techniques via RLHF", "summary": "Reinforcement learning from human feedback"},
    ]
    
    # We query for an unrelated term so that keyword matching score is 0,
    # but the watchlist should pick up c2 because it's related to the watchlist item.
    report = radar.generate_daily_digest(
        category_or_query="quantum computing",
        candidate_papers=candidates,
        top_k=2
    )
    
    assert len(report.matched_papers) > 0
    # The RLHF paper should have a higher score due to watchlist match
    assert report.matched_papers[0]["id"] == "c2"

def test_no_matches():
    radar = ArxivRadar()
    candidates = [
        {"id": "c1", "title": "Apples", "summary": "Red fruit"},
    ]
    report = radar.generate_daily_digest(
        category_or_query="quantum",
        candidate_papers=candidates,
        top_k=5
    )
    assert len(report.matched_papers) == 0
    assert "No highly relevant papers matched" in report.executive_briefing