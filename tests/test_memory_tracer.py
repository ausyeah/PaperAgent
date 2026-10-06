import pytest
from datetime import datetime

from paperagent.models import PaperProject, ParsedPaper, PaperMetadata
from paperagent.synthesizer.memory_tracer import MemoryTracer

def test_memory_tracer_optimal():
    tracer = MemoryTracer()
    # 100M parameters -> Should be Optimal
    mock_paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper Small"),
        raw_markdown="This model has 100M parameters and uses standard linear layers."
    )
    project = PaperProject(id="1", paper=mock_paper)
    
    profile = tracer.profile_memory(project)
    
    assert profile.module_name == "Test Paper Small"
    assert profile.parameter_memory_mb == 400.0  # 100 * 4
    assert profile.activation_memory_mb == 800.0 # 100 * 8
    assert profile.peak_memory_mb == 2400.0      # 400 + 800 + 400 + 800
    assert profile.memory_efficiency_verdict == "Optimal"
    assert len(profile.events) == 4
    assert profile.events[0].operation_name == "Load Model Parameters (FP32)"
    assert profile.events[3].operation_name == "Optimizer Step (Adam)"
    assert any("comfortably" in rec for rec in profile.optimization_recommendations)

def test_memory_tracer_moderate():
    tracer = MemoryTracer()
    # 3B parameters -> Moderate (72000 MB peak? wait: 3000 * 24 = 72000... 
    # Ah, wait, if 3000M params -> peak memory is 3000 * 24 = 72,000MB.
    # 72,000 MB > 24,000, so it will be High VRAM Overhead.
    # Let's test moderate: peak needs to be between 8000 and 24000.
    # So peak = param * 24.
    # To get ~15000 peak, param = ~600M. Let's use 600M.
    mock_paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper Moderate"),
        raw_markdown="This model has 600M parameters."
    )
    project = PaperProject(id="2", paper=mock_paper)
    
    profile = tracer.profile_memory(project)
    
    assert profile.memory_efficiency_verdict == "Moderate"
    assert profile.peak_memory_mb == 14400.0
    assert any("FP16" in rec for rec in profile.optimization_recommendations)

def test_memory_tracer_high_vram_and_attention():
    tracer = MemoryTracer()
    # 7B parameters -> High VRAM
    mock_paper = ParsedPaper(
        metadata=PaperMetadata(title="Test Paper Huge"),
        raw_markdown="We present a large language model with 7B parameters using flash attention."
    )
    project = PaperProject(id="3", paper=mock_paper)
    
    profile = tracer.profile_memory(project)
    
    assert profile.memory_efficiency_verdict == "High VRAM Overhead"
    assert profile.peak_memory_mb == 168000.0 # 7000 * 24
    assert any("Flash Attention" in rec for rec in profile.optimization_recommendations)
    assert any("LoRA" in rec for rec in profile.optimization_recommendations)