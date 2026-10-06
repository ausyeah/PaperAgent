import pytest
from paperagent.runner.self_debugger import SelfHealingDebugger
from paperagent.models import SelfHealingResult

def test_self_debugger_success():
    debugger = SelfHealingDebugger()
    code = "print('Hello World')"
    result = debugger.heal_code(code)
    
    assert isinstance(result, SelfHealingResult)
    assert result.success is True
    assert result.iterations_run == 1
    assert len(result.patches) == 0
    assert "Hello World" in result.final_stdout

def test_self_debugger_heals_missing_numpy():
    debugger = SelfHealingDebugger()
    code = "x = np.array([1, 2, 3])\nprint(x.sum())"
    result = debugger.heal_code(code, max_iterations=3)
    
    assert isinstance(result, SelfHealingResult)
    assert result.success is True
    assert len(result.patches) >= 1
    assert result.patches[0].error_type == "NameError"
    assert "numpy" in result.patches[0].patch_applied
    assert "6" in result.final_stdout

def test_self_debugger_heals_missing_math():
    debugger = SelfHealingDebugger()
    code = "print(math.sqrt(16))"
    result = debugger.heal_code(code, max_iterations=3)
    
    assert isinstance(result, SelfHealingResult)
    assert result.success is True
    assert len(result.patches) >= 1
    assert "math" in result.patches[0].patch_applied
    assert "4.0" in result.final_stdout

def test_self_debugger_unhealable():
    debugger = SelfHealingDebugger()
    code = "1 / 0"
    result = debugger.heal_code(code, max_iterations=2)
    
    assert isinstance(result, SelfHealingResult)
    assert result.success is False
