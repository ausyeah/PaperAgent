import re
from typing import Dict, Optional, List
from pydantic import BaseModel

from paperagent.models import ParsedPaper, LeaderboardSnapshot, BenchmarkMetricRecord

class LeaderboardTracker:
    def __init__(self):
        # Base SOTA scores to track against if not provided via custom_benchmarks
        self.default_sota = {
            "ImageNet Top-1": 91.1,
            "GLUE": 91.3,
            "MMLU": 89.0,
            "GSM8K": 96.3
        }

    def track_paper_performance(self, paper: ParsedPaper, custom_benchmarks: Optional[Dict[str, float]] = None) -> LeaderboardSnapshot:
        benchmarks = self.default_sota.copy()
        if custom_benchmarks:
            benchmarks.update(custom_benchmarks)
        
        metrics = []
        raw_text = paper.raw_markdown or ""
        
        for benchmark_name, sota_score in benchmarks.items():
            # Basic regex to find mention of the benchmark followed by a number
            # e.g., "MMLU: 90.5", "achieved 90.5 on MMLU", "MMLU accuracy of 90.5%"
            # This is a simple heuristic fallback for extraction.
            # Look for the benchmark name, then optional words (max 5), then a float/int
            pattern = rf"{re.escape(benchmark_name)}(?:[^\d\.\n]{{0,30}}?)([\d]+\.[\d]+|[\d]+)"
            match = re.search(pattern, raw_text, re.IGNORECASE)
            
            if match:
                try:
                    paper_score = float(match.group(1))
                    
                    relative_gap_pct = ((paper_score - sota_score) / sota_score) * 100
                    is_new_sota = paper_score > sota_score
                    
                    metrics.append(BenchmarkMetricRecord(
                        benchmark_name=benchmark_name,
                        sota_score=sota_score,
                        paper_score=paper_score,
                        relative_gap_pct=relative_gap_pct,
                        is_new_sota=is_new_sota
                    ))
                except ValueError:
                    pass
        
        # Calculate saturation verdict based on metrics
        saturation_verdict = "Active Competition"
        if metrics:
            # If any metric is near ceiling (e.g. SOTA > 95)
            # Or gap is extremely small for high SOTA
            
            # Simple heuristic
            is_ceiling = any(m.sota_score >= 95.0 for m in metrics)
            is_breakthrough = any(m.is_new_sota and m.sota_score < 90.0 and (m.paper_score - m.sota_score) > 5.0 for m in metrics)
            
            if is_breakthrough:
                saturation_verdict = "Early Breakthrough"
            elif is_ceiling:
                saturation_verdict = "Approaching Ceiling"
                
        snapshot = LeaderboardSnapshot(
            paper_title=paper.metadata.title,
            metrics=metrics,
            saturation_verdict=saturation_verdict
        )
        return snapshot