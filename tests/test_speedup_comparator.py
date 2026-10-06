from paperagent.engine.speedup_comparator import SpeedupComparator
from paperagent.models import SpeedupComparisonResult

def test_speedup_comparator():
    comparator = SpeedupComparator()
    result = comparator.compare_framework_runtimes(algorithm_name="test_algo")
    
    assert isinstance(result, SpeedupComparisonResult)
    assert result.algorithm_name == "test_algo"
    assert "pytorch" in result.framework_latencies_ms
    assert "jax" in result.framework_latencies_ms
    assert "triton" in result.framework_latencies_ms
    
    assert "jax" in result.speedup_ratios
    assert "triton" in result.speedup_ratios
    
    assert result.fastest_framework in ["pytorch", "jax", "triton"]
    assert isinstance(result.efficiency_notes, str)