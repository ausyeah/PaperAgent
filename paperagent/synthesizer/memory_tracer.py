from typing import List, Optional
import re

from paperagent.models import PaperProject, MemoryTraceProfile, MemoryAllocationEvent
from paperagent.synthesizer.hardware_estimator import HardwareEstimator


class MemoryTracer:
    """Granular Peak Memory Profiler and Allocation Snapshot Generator."""

    def __init__(self):
        self.hardware_estimator = HardwareEstimator()

    def profile_memory(self, project: PaperProject) -> MemoryTraceProfile:
        """
        Models tensor memory allocation per operator/layer based on paper parameters and batch shapes.
        Calculates peak memory MB, activation memory MB, parameter memory MB.
        Generates itemized MemoryAllocationEvent items and memory efficiency verdicts.
        Outputs concrete actionable optimization recommendations.
        """
        module_name = project.paper.metadata.title
        text = project.paper.raw_markdown

        # Infer parameter count
        param_count_m = self.hardware_estimator._infer_param_count_from_text(text)
        if param_count_m is None:
            param_count_m = 100.0  # Default to 100M if not found

        # Calculate memory (rough heuristic models for demonstration)
        # FP32 weights -> 4 bytes per param
        parameter_memory_mb = param_count_m * 4.0
        
        # Assume activations are roughly 2x parameter memory for a standard forward pass
        activation_memory_mb = param_count_m * 8.0

        # Gradients and optimizer states (Adam -> 8 bytes/param)
        gradients_memory_mb = param_count_m * 4.0
        optimizer_memory_mb = param_count_m * 8.0

        peak_memory_mb = parameter_memory_mb + activation_memory_mb + gradients_memory_mb + optimizer_memory_mb

        # Generate Events
        events: List[MemoryAllocationEvent] = []
        
        # Event 1: Model parameters
        events.append(MemoryAllocationEvent(
            operation_name="Load Model Parameters (FP32)",
            allocated_mb=round(parameter_memory_mb, 2),
            peak_mb=round(parameter_memory_mb, 2),
            notes=f"Loaded {param_count_m}M parameters"
        ))

        # Event 2: Forward pass (Activations)
        current_peak = parameter_memory_mb + activation_memory_mb
        events.append(MemoryAllocationEvent(
            operation_name="Forward Pass (Activations)",
            allocated_mb=round(activation_memory_mb, 2),
            peak_mb=round(current_peak, 2),
            notes="Stored activations for backward pass"
        ))

        # Event 3: Backward pass (Gradients)
        current_peak += gradients_memory_mb
        events.append(MemoryAllocationEvent(
            operation_name="Backward Pass (Gradients)",
            allocated_mb=round(gradients_memory_mb, 2),
            peak_mb=round(current_peak, 2),
            notes="Computed gradients for parameters"
        ))

        # Event 4: Optimizer step
        current_peak += optimizer_memory_mb
        events.append(MemoryAllocationEvent(
            operation_name="Optimizer Step (Adam)",
            allocated_mb=round(optimizer_memory_mb, 2),
            peak_mb=round(current_peak, 2),
            notes="Allocated optimizer momentum/variance states"
        ))

        # Determine verdict
        if peak_memory_mb < 8000:
            memory_efficiency_verdict = "Optimal"
        elif peak_memory_mb < 24000:
            memory_efficiency_verdict = "Moderate"
        else:
            memory_efficiency_verdict = "High VRAM Overhead"

        # Generate recommendations
        recommendations = []
        if memory_efficiency_verdict in ["Moderate", "High VRAM Overhead"]:
            recommendations.append("Use FP16 or BF16 mixed precision to halve parameter and gradient memory.")
            recommendations.append("Implement Gradient Checkpointing to trade compute for reduced activation memory.")
            if param_count_m > 1000:
                recommendations.append("Consider LoRA or other PEFT methods if full fine-tuning is not required.")
                recommendations.append("Use 8-bit or 4-bit quantization (e.g., bitsandbytes) for optimizer states.")
        else:
            recommendations.append("Current memory footprint fits comfortably within standard consumer GPUs.")
            recommendations.append("Consider increasing batch size to maximize GPU utilization.")

        if "attention" in text.lower():
             recommendations.append("Integrate Flash Attention to reduce attention matrix activation memory.")

        return MemoryTraceProfile(
            module_name=module_name,
            peak_memory_mb=round(peak_memory_mb, 2),
            activation_memory_mb=round(activation_memory_mb, 2),
            parameter_memory_mb=round(parameter_memory_mb, 2),
            events=events,
            memory_efficiency_verdict=memory_efficiency_verdict,
            optimization_recommendations=recommendations
        )