import os
import tempfile
from unittest.mock import Mock

import pytest

from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, PodcastScript, PodcastDialogueTurn, AnalysisReport, ReviewerCritique
from paperagent.export.audio_script import generate_podcast_script, export_podcast_script_file
from paperagent.engine.llm_client import LLMClient


@pytest.fixture
def mock_project():
    return PaperProject(
        id="test-proj-123",
        paper=ParsedPaper(
            metadata=PaperMetadata(
                title="Test Paper Title",
                authors=["Author A", "Author B"],
                year=2024
            ),
            sections=[],
            references=[]
        ),
        analysis=AnalysisReport(
            executive_summary="This is a dummy executive summary.",
            methodology_overview="Dummy methodology overview.",
            core_problem="Dummy core problem",
            key_innovation="Dummy key innovation",
            reviewer_critique=ReviewerCritique(
                strengths=["Strength A"],
                weaknesses=["Weakness B"],
                boundary_conditions=[],
                potential_reproducibility_pitfalls=[],
                score=8
            )
        )
    )

def test_generate_podcast_script_fallback(mock_project):
    script = generate_podcast_script(mock_project, client=None)
    
    assert isinstance(script, PodcastScript)
    assert script.episode_title == "Deep Dive: Test Paper Title"
    assert "Alex (Explorer)" in script.hosts
    assert "Morgan (Specialist)" in script.hosts
    
    # Check turns
    assert len(script.turns) > 0
    
    # Check speaker alternation
    speakers = [t.speaker for t in script.turns]
    assert speakers[0] == "Alex (Explorer)"
    assert speakers[1] == "Morgan (Specialist)"
    assert speakers[2] == "Alex (Explorer)"
    
    # Check timing
    assert script.total_duration_minutes > 0
    total_seconds = sum(t.timing_seconds for t in script.turns)
    assert script.total_duration_minutes == round(total_seconds / 60.0, 2)
    
    # Check markdown
    assert "Audio Script: Deep Dive: Test Paper Title" in script.audio_briefing_markdown
    assert "This is a dummy executive summary" in script.audio_briefing_markdown
    assert "Dummy methodology overview" in script.audio_briefing_markdown

def test_generate_podcast_script_llm(mock_project):
    mock_client = Mock(spec=LLMClient)
    
    # Mock LLM generation result
    mock_script = PodcastScript(
        episode_title="Mocked Episode",
        hosts=["Alice (Explorer)", "Bob (Specialist)"],
        turns=[
            PodcastDialogueTurn(speaker="Alice (Explorer)", speech="Hello!", timing_seconds=5),
            PodcastDialogueTurn(speaker="Bob (Specialist)", speech="Hi there!", timing_seconds=5)
        ]
    )
    mock_client.generate_structured.return_value = mock_script
    
    script = generate_podcast_script(mock_project, client=mock_client)
    
    assert isinstance(script, PodcastScript)
    assert script.episode_title == "Mocked Episode"
    assert len(script.turns) == 2
    assert script.total_duration_minutes == round(10 / 60.0, 2)
    assert "Mocked Episode" in script.audio_briefing_markdown

def test_export_podcast_script_file(mock_project):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "script.md")
        returned_path = export_podcast_script_file(mock_project, output_path)
        
        assert returned_path == output_path
        assert os.path.exists(output_path)
        
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        assert "Deep Dive: Test Paper Title" in content
        assert "Alex (Explorer)" in content