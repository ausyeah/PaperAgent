import pytest
from paperagent.engine.gradient_verifier import GradientVerifier
from paperagent.models import GradientVerificationReport

def test_verify_linear_function():
    code = """
def linear(x):
    return 2 * x + 3
"""
    verifier = GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=4)
    
    assert isinstance(report, GradientVerificationReport)
    assert report.all_passed is True
    assert report.gradient_health == "Healthy"
    assert len(report.checks) == 1
    assert report.checks[0].relative_difference < 1e-3
    assert report.checks[0].is_differentiable is True

def test_verify_quadratic_function():
    code = """
def quadratic(x):
    return x ** 2 + 5 * x
"""
    verifier = GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=2)
    
    assert isinstance(report, GradientVerificationReport)
    assert report.all_passed is True
    assert report.gradient_health == "Healthy"

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch is not installed")
def test_verify_sigmoid_function():
    code = """
import torch
def sigmoid(x):
    return torch.sigmoid(x)
"""
    verifier = GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=5)
    
    assert isinstance(report, GradientVerificationReport)
    assert report.all_passed is True

@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch is not installed")
def test_verify_nn_module():
    code = """
import torch.nn as nn
class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(4, 2)
        
    def forward(self, x):
        return self.linear(x) ** 2
"""
    verifier = GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=4)
    
    assert isinstance(report, GradientVerificationReport)
    assert report.all_passed is True
    assert len(report.checks) == 2 # weight and bias

@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch is not installed")
def test_gradient_anomaly_non_differentiable():
    code = """
import torch
def non_diff(x):
    return torch.round(x)
"""
    verifier = GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=3)
    
    assert isinstance(report, GradientVerificationReport)
    assert report.all_passed is False
    assert report.gradient_health == "Anomalous"

@pytest.mark.skipif(not HAS_TORCH, reason="PyTorch is not installed")
def test_gradient_anomaly_nan():
    # If the function itself returns NaN, gradient will be NaN. Let's make an anomaly
    code = """
import torch
def nan_grad(x):
    return x / 0.0
"""
    verifier = GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=2)
    
    assert report.all_passed is False


def test_no_callable_found():
    code = "x = 5"
    verifier = GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=2)
    
    assert report.all_passed is False
    assert report.summary_notes == "Could not extract a callable from the provided code."

def test_numpy_fallback(monkeypatch):
    import paperagent.engine.gradient_verifier as gv
    monkeypatch.setattr(gv, "HAS_TORCH", False)
    
    code = """
import numpy as np
def f(x):
    return np.sum(x ** 2)
"""
    verifier = gv.GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=3)
    
    assert report.all_passed is True
    assert report.gradient_health == "Healthy"
    assert "NumPy fallback" in report.summary_notes

def test_numpy_fallback_anomaly(monkeypatch):
    import paperagent.engine.gradient_verifier as gv
    monkeypatch.setattr(gv, "HAS_TORCH", False)
    
    code = """
import numpy as np
def f(x):
    return np.sum(np.round(x))
"""
    verifier = gv.GradientVerifier()
    report = verifier.verify_gradients(code, input_dim=3)
    
    assert report.all_passed is False
    assert report.gradient_health == "Anomalous"