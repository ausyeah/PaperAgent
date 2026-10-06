import pytest
from paperagent.models import ParsedPaper, PaperMetadata, PaperSection
from paperagent.storage.leaderboard import LeaderboardTracker

@pytest.fixture
def base_paper():
    metadata = PaperMetadata(title="Test Paper", authors=[], abstract="", year=2024, url="", arxiv_id="")
    return ParsedPaper(metadata=metadata, sections=[], raw_markdown="")

def test_metric_matching(base_paper):
    # Test that regex successfully pulls out the paper score
    base_paper.raw_markdown = "We evaluate on MMLU and achieve 90.5 accuracy. On GSM8K, we get 97.2%."
    tracker = LeaderboardTracker()
    snapshot = tracker.track_paper_performance(base_paper)
    
    assert len(snapshot.metrics) == 2
    
    mmlu_metric = next((m for m in snapshot.metrics if m.benchmark_name.lower() == "mmlu"), None)
    assert mmlu_metric is not None
    assert mmlu_metric.paper_score == 90.5
    
    gsm8k_metric = next((m for m in snapshot.metrics if m.benchmark_name.lower() == "gsm8k"), None)
    assert gsm8k_metric is not None
    assert gsm8k_metric.paper_score == 97.2

def test_gap_calculation(base_paper):
    base_paper.raw_markdown = "Our new model reaches an ImageNet Top-1 of 92.0."
    tracker = LeaderboardTracker()
    # Provide custom baseline for deterministic testing
    snapshot = tracker.track_paper_performance(base_paper, custom_benchmarks={"ImageNet Top-1": 90.0})
    
    assert len(snapshot.metrics) == 1
    metric = snapshot.metrics[0]
    assert metric.paper_score == 92.0
    assert metric.sota_score == 90.0
    
    expected_gap = ((92.0 - 90.0) / 90.0) * 100
    assert pytest.approx(metric.relative_gap_pct, 0.001) == expected_gap

def test_sota_flagging(base_paper):
    base_paper.raw_markdown = "GLUE score is 90.0. MMLU is 95.0."
    tracker = LeaderboardTracker()
    snapshot = tracker.track_paper_performance(base_paper, custom_benchmarks={"GLUE": 91.0, "MMLU": 89.0})
    
    glue_metric = next((m for m in snapshot.metrics if m.benchmark_name.lower() == "glue"), None)
    assert glue_metric.is_new_sota is False
    
    mmlu_metric = next((m for m in snapshot.metrics if m.benchmark_name.lower() == "mmlu"), None)
    assert mmlu_metric.is_new_sota is True

def test_saturation_detection_active(base_paper):
    base_paper.raw_markdown = "MMLU is 89.5."
    tracker = LeaderboardTracker()
    snapshot = tracker.track_paper_performance(base_paper, custom_benchmarks={"MMLU": 89.0})
    
    assert snapshot.saturation_verdict == "Active Competition"

def test_saturation_detection_ceiling(base_paper):
    base_paper.raw_markdown = "GSM8K score of 98.0."
    tracker = LeaderboardTracker()
    # Set sota_score to >= 95.0 to trigger 'Approaching Ceiling'
    snapshot = tracker.track_paper_performance(base_paper, custom_benchmarks={"GSM8K": 96.0})
    
    assert snapshot.saturation_verdict == "Approaching Ceiling"

def test_saturation_detection_breakthrough(base_paper):
    base_paper.raw_markdown = "New Dataset score is 60.0."
    tracker = LeaderboardTracker()
    # sota < 90, gap > 5 -> breakthrough
    snapshot = tracker.track_paper_performance(base_paper, custom_benchmarks={"New Dataset": 50.0})
    
    assert snapshot.saturation_verdict == "Early Breakthrough"

def test_custom_benchmarks_only(base_paper):
    base_paper.raw_markdown = "CustomBench score is 100.0."
    tracker = LeaderboardTracker()
    
    snapshot = tracker.track_paper_performance(base_paper, custom_benchmarks={"CustomBench": 50.0})
    
    metric = next((m for m in snapshot.metrics if m.benchmark_name == "CustomBench"), None)
    assert metric is not None
    assert metric.paper_score == 100.0
    assert metric.sota_score == 50.0