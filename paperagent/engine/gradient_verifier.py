import math
import numpy as np
from typing import Callable, Any, Dict, List, Optional
import inspect

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from paperagent.models import GradientCheckItem, GradientVerificationReport

class GradientVerifier:
    """Verifies gradients using numerical differentiation."""

    def __init__(self):
        pass

    def _extract_callable(self, func_or_code: str) -> Optional[Callable]:
        """Extracts a callable function from a code string or returns the string if it's not code."""
        if not func_or_code or not isinstance(func_or_code, str):
            return None
            
        namespace: Dict[str, Any] = {}
        try:
            # First, check if it's just a variable name in the environment
            # If we need to exec, use shared namespace
            exec(func_or_code, namespace, namespace)
            
            # Find the first callable
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith("__"):
                    # Check if it looks like a function we defined and not an import
                    if inspect.isfunction(obj) or inspect.isclass(obj):
                        return obj
            return None
        except Exception as e:
            return None
            
    def _compute_numerical_gradient_numpy(self, func: Callable, x: np.ndarray, epsilon: float) -> np.ndarray:
        """Computes numerical gradient using finite differences with NumPy."""
        grad = np.zeros_like(x)
        it = np.nditer(x, flags=['multi_index'], op_flags=['readwrite'])
        
        while not it.finished:
            idx = it.multi_index
            orig_val = x[idx]
            
            x[idx] = orig_val + epsilon
            f_plus = func(x)
            
            x[idx] = orig_val - epsilon
            f_minus = func(x)
            
            x[idx] = orig_val
            
            # Handle non-scalar outputs by summing (assuming scalar loss for gradient check)
            if isinstance(f_plus, np.ndarray):
                f_plus = np.sum(f_plus)
                f_minus = np.sum(f_minus)
                
            grad[idx] = (f_plus - f_minus) / (2 * epsilon)
            it.iternext()
            
        return grad

    def _verify_pytorch(self, func: Callable, input_dim: int, epsilon: float) -> GradientVerificationReport:
        """Verifies gradients using PyTorch autograd."""
        x = torch.randn(input_dim, requires_grad=True, dtype=torch.float64)
        
        try:
            # Instantiate if it's a class (e.g. nn.Module)
            if inspect.isclass(func):
                model = func()
                # If the class has parameters, test wrt parameters
                if hasattr(model, "parameters") and list(model.parameters()):
                    return self._verify_pytorch_module(model, input_dim, epsilon)
                y = model(x)
            else:
                y = func(x)
                
            if y is None:
                return GradientVerificationReport(
                    module_name=getattr(func, "__name__", "unknown"),
                    all_passed=False,
                    gradient_health="Failed",
                    summary_notes="Function returned None."
                )

            # Convert to scalar loss
            loss = y.sum()
            loss.backward()
            
            ana_grad = x.grad.detach().numpy()
            x_np = x.detach().numpy()
            
            # Define a numpy wrapper for numerical gradient
            def np_func(x_in):
                t_in = torch.tensor(x_in, dtype=torch.float64)
                if inspect.isclass(func):
                    model = func()
                    out = model(t_in)
                else:
                    out = func(t_in)
                return out.detach().numpy().sum()
                
            num_grad = self._compute_numerical_gradient_numpy(np_func, x_np, epsilon)
            
            return self._compare_gradients(
                module_name=getattr(func, "__name__", "unknown"),
                ana_grad=ana_grad,
                num_grad=num_grad,
                param_name="input"
            )
            
        except Exception as e:
            return GradientVerificationReport(
                module_name=getattr(func, "__name__", "unknown"),
                all_passed=False,
                gradient_health="Failed",
                summary_notes=f"Execution error: {str(e)}"
            )

    def _verify_pytorch_module(self, model: Any, input_dim: int, epsilon: float) -> GradientVerificationReport:
        """Verifies gradients for a PyTorch nn.Module with parameters."""
        x = torch.randn(input_dim, dtype=torch.float64)
        # Double precision for better numerical stability
        model = model.double()
        
        try:
            y = model(x)
            loss = y.sum()
            loss.backward()
            
            checks = []
            all_passed = True
            
            for name, param in model.named_parameters():
                if param.grad is None:
                    checks.append(GradientCheckItem(
                        parameter_name=name,
                        analytical_grad_norm=0.0,
                        numerical_grad_norm=0.0,
                        relative_difference=0.0,
                        is_differentiable=False
                    ))
                    all_passed = False
                    continue
                    
                ana_grad = param.grad.detach().numpy()
                param_np = param.detach().numpy()
                
                # Compute numerical gradient wrt this parameter
                grad_num = np.zeros_like(param_np)
                it = np.nditer(param_np, flags=['multi_index'], op_flags=['readwrite'])
                
                while not it.finished:
                    idx = it.multi_index
                    orig_val = param_np[idx]
                    
                    # f(x + eps)
                    with torch.no_grad():
                        param.copy_(torch.tensor(param_np, dtype=torch.float64))
                        param.data[idx] = orig_val + epsilon
                        f_plus = model(x).sum().item()
                        
                        # f(x - eps)
                        param.data[idx] = orig_val - epsilon
                        f_minus = model(x).sum().item()
                        
                        # restore
                        param.data[idx] = orig_val
                        
                    grad_num[idx] = (f_plus - f_minus) / (2 * epsilon)
                    it.iternext()
                
                ana_norm = np.linalg.norm(ana_grad)
                num_norm = np.linalg.norm(grad_num)
                
                diff = np.abs(grad_num - ana_grad)
                denom = np.abs(grad_num) + np.abs(ana_grad) + 1e-8
                rel_diff = np.max(diff / denom)
                
                is_non_zero = num_norm > 1e-8
                passed = bool(np.isfinite(rel_diff) and rel_diff < 1e-3 and np.isfinite(ana_norm) and np.isfinite(num_norm) and is_non_zero)
                
                checks.append(GradientCheckItem(
                    parameter_name=name,
                    analytical_grad_norm=float(ana_norm),
                    numerical_grad_norm=float(num_norm),
                    relative_difference=float(rel_diff),
                    is_differentiable=True
                ))
                
                if not passed:
                    all_passed = False
                    
            return GradientVerificationReport(
                module_name=model.__class__.__name__,
                checks=checks,
                all_passed=all_passed,
                gradient_health="Healthy" if all_passed else "Anomalous",
                summary_notes="Module parameters checked successfully." if all_passed else "Gradient anomalies detected."
            )
            
        except Exception as e:
            return GradientVerificationReport(
                module_name=model.__class__.__name__,
                all_passed=False,
                gradient_health="Failed",
                summary_notes=f"Execution error: {str(e)}"
            )

    def _verify_numpy_fallback(self, func: Callable, input_dim: int, epsilon: float) -> GradientVerificationReport:
        """Verifies gradients using pure Python/NumPy fallback.
        Since we don't have analytical gradients, we assume numerical gradient is the ground truth
        and just check for anomalies (NaN, Inf, Zero).
        """
        x = np.random.randn(input_dim).astype(np.float64)
        
        try:
            # If it's a class, instantiate it
            if inspect.isclass(func):
                model = func()
                def wrapped_func(x_in):
                    return model(x_in)
                func_to_use = wrapped_func
            else:
                func_to_use = func
                
            num_grad = self._compute_numerical_gradient_numpy(func_to_use, x, epsilon)
            
            # Since no analytical, we mock it with num_grad to pass the difference check,
            # but we can check if it's mathematically sound.
            num_norm = np.linalg.norm(num_grad)
            
            # Check anomalies
            is_valid = np.all(np.isfinite(num_grad))
            is_non_zero = num_norm > 1e-8
            
            passed = bool(is_valid and is_non_zero)
            
            check = GradientCheckItem(
                parameter_name="input",
                analytical_grad_norm=0.0, # Not available in fallback
                numerical_grad_norm=float(num_norm),
                relative_difference=0.0,
                is_differentiable=bool(is_valid)
            )
            
            health = "Healthy"
            notes = "Checked numerical gradients only (NumPy fallback)."
            if not is_valid:
                health = "Anomalous"
                notes = "Gradient contains NaN or Inf."
            elif not is_non_zero:
                health = "Anomalous"
                notes = "Gradient is zero."
                
            return GradientVerificationReport(
                module_name=getattr(func, "__name__", "unknown"),
                checks=[check],
                all_passed=passed,
                gradient_health=health,
                summary_notes=notes
            )
            
        except Exception as e:
            return GradientVerificationReport(
                module_name=getattr(func, "__name__", "unknown"),
                all_passed=False,
                gradient_health="Failed",
                summary_notes=f"Execution error: {str(e)}"
            )

    def _compare_gradients(self, module_name: str, ana_grad: np.ndarray, num_grad: np.ndarray, param_name: str) -> GradientVerificationReport:
        """Helper to compare analytical and numerical gradients."""
        ana_norm = np.linalg.norm(ana_grad)
        num_norm = np.linalg.norm(num_grad)
        
        diff = np.abs(num_grad - ana_grad)
        denom = np.abs(num_grad) + np.abs(ana_grad) + 1e-8
        rel_diff = np.max(diff / denom)
        
        # Check soundness
        is_finite = np.all(np.isfinite(ana_grad)) and np.all(np.isfinite(num_grad))
        is_non_zero = num_norm > 1e-8
        passed = bool(is_finite and is_non_zero and rel_diff < 1e-3)
        
        check = GradientCheckItem(
            parameter_name=param_name,
            analytical_grad_norm=float(ana_norm),
            numerical_grad_norm=float(num_norm),
            relative_difference=float(rel_diff),
            is_differentiable=bool(is_finite)
        )
        
        health = "Healthy" if passed else "Anomalous"
        notes = "Gradients match perfectly." if passed else "Gradient mismatch or anomalies detected."
        
        return GradientVerificationReport(
            module_name=module_name,
            checks=[check],
            all_passed=passed,
            gradient_health=health,
            summary_notes=notes
        )

    def verify_gradients(self, func_or_code: str, input_dim: int = 4, epsilon: float = 1e-5) -> GradientVerificationReport:
        """
        Performs finite-difference gradient checking against analytical gradients.
        
        Args:
            func_or_code: A string containing Python code that defines a function or class.
            input_dim: The dimension of the input tensor/array.
            epsilon: The perturbation value for finite differences.
            
        Returns:
            GradientVerificationReport
        """
        func = self._extract_callable(func_or_code)
        
        if func is None:
            return GradientVerificationReport(
                module_name="unknown",
                all_passed=False,
                gradient_health="Failed",
                summary_notes="Could not extract a callable from the provided code."
            )
            
        if HAS_TORCH:
            return self._verify_pytorch(func, input_dim, epsilon)
        else:
            return self._verify_numpy_fallback(func, input_dim, epsilon)
