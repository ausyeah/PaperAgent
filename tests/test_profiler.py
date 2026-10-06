import pytest
from paperagent.synthesizer.profiler import ComplexityProfiler

def test_profiler_linear():
    profiler = ComplexityProfiler()
    # A linear algorithm
    code = """
def run(N):
    total = 0
    # Add a small delay to make latency measurable
    import time
    for i in range(N):
        total += i
        time.sleep(0.001)
    return total
"""
    result = profiler.profile_code(code, scales=[10, 20, 40], timeout_per_scale=5.0)

    assert result.algorithm_name == "Custom Algorithm"
    assert len(result.measurements) == 3
    assert result.measurements[0].input_scale == 10
    assert result.measurements[1].input_scale == 20
    assert result.measurements[2].input_scale == 40
    assert result.empirical_scaling == "O(N) Linear"

def test_profiler_quadratic():
    profiler = ComplexityProfiler()
    # A quadratic algorithm
    code = """
def run(N):
    total = 0
    import time
    for i in range(N):
        for j in range(N):
            total += 1
            time.sleep(0.0005)
    return total
"""
    result = profiler.profile_code(code, scales=[10, 20, 30], timeout_per_scale=10.0)

    assert result.algorithm_name == "Custom Algorithm"
    assert len(result.measurements) == 3
    assert result.measurements[0].input_scale == 10
    assert result.measurements[1].input_scale == 20
    assert result.measurements[2].input_scale == 30
    assert result.empirical_scaling == "O(N^2) Quadratic"

def test_profiler_fallback():
    profiler = ComplexityProfiler()
    # Malformed code to trigger fallback
    code = """
def run(N):
    raise ValueError("Intentional error")
"""
    result = profiler.profile_code(code, scales=[10, 20])

    assert result.algorithm_name == "Fallback Algorithm"
    assert result.empirical_scaling == "O(N) Linear"
    assert "Execution failed" in result.bottleneck_analysis
