import re
from typing import Optional

from paperagent.models import PaperProject, QuantizationBenchmarkRow, QuantizationProfile

class PrecisionQuantizer:
    """Post-Training Quantization and Precision Profiler."""

    def __init__(self):
        pass


    def profile_quantization(self, project: PaperProject) -> QuantizationProfile:
        """
        Models and profiles model footprints across FP32, FP16, BF16, INT8, and INT4 precision.
        Calculates theoretical memory footprint (MB) and expected latency scaling.
        Generates PyTorch dynamic quantization wrapper code.
        Recommends optimal precision.
        """
        model_name = project.paper.metadata.title

        # Try to infer parameter count from paper markdown, default to 100M
        param_count_m = self._infer_param_count_from_text(project.paper.raw_markdown)
        if param_count_m is None:
            param_count_m = 100.0
            
        precision_rows = []
        
        # Define precisions and their bytes per parameter
        precisions = [
            ("FP32", 4.0, 1.0, 1.0),     # Baseline
            ("FP16", 2.0, 0.6, 1.0),     # Faster, slight perplexity hit (usually negligible for modern models)
            ("BF16", 2.0, 0.6, 1.0),     # Better dynamic range
            ("INT8", 1.0, 0.4, 1.05),    # INT8 Weight-Only / Activation, visible perplexity change sometimes
            ("INT4", 0.5, 0.25, 1.15)    # INT4 Weight-Only, higher perplexity hit
        ]
        
        for name, bytes_per_param, latency_scale, perp_scale in precisions:
            # Memory in MB
            memory_mb = param_count_m * bytes_per_param
            
            # Baseline latency is completely arbitrary here without hardware, we just use latency_scale
            # For a 100M model maybe latency is ~50ms in FP32 on some CPU
            latency_ms = 50.0 * latency_scale 
            
            precision_rows.append(QuantizationBenchmarkRow(
                precision=name,
                memory_mb=round(memory_mb, 2),
                latency_ms=round(latency_ms, 2),
                relative_perplexity=round(perp_scale, 2)
            ))
            
        # Recommended precision logic
        if param_count_m > 10000.0:  # > 10B
            recommended = "INT4 Weight-Only"
        elif param_count_m > 1000.0: # > 1B
            recommended = "INT8 Weight-Only"
        else:
            recommended = "FP16 / BF16"
            
        wrapper_code = self._generate_wrapper_code(model_name, recommended)

        return QuantizationProfile(
            model_name=model_name,
            precision_rows=precision_rows,
            wrapper_code=wrapper_code,
            recommended_precision=recommended
        )

    def _infer_param_count_from_text(self, text: str) -> Optional[float]:
        """Try to parse parameter count (e.g. 7B, 110M) from markdown."""
        if not text:
            return None
            
        b_match = re.search(r'(\d+(?:\.\d+)?)[mMbB]\s*(?:parameters|params)', text, re.IGNORECASE)
        if b_match:
            val = float(b_match.group(1))
            if 'B' in b_match.group(0).upper() or 'b' in b_match.group(0):
                return val * 1000.0
            return val
            
        return None

    def _generate_wrapper_code(self, model_name: str, recommended_precision: str) -> str:
        code = f'''import torch
import torch.nn as nn
import torch.ao.quantization

# Auto-generated Quantization Wrapper for {model_name}
# Recommended Precision: {recommended_precision}

def apply_dynamic_quantization(model: nn.Module) -> nn.Module:
    """
    Applies dynamic post-training quantization to the model.
    By default, targets nn.Linear layers for INT8 quantization.
    """
    model.eval()
    
    # Define qconfig for dynamic quantization
    qconfig_spec = {{
        nn.Linear: torch.ao.quantization.default_dynamic_qconfig
    }}
    
    # Apply dynamic quantization
    quantized_model = torch.ao.quantization.quantize_dynamic(
        model,
        qconfig_spec,
        dtype=torch.qint8
    )
    
    return quantized_model

if __name__ == "__main__":
    # Example usage:
    # class DummyModel(nn.Module):
    #     def __init__(self):
    #         super().__init__()
    #         self.fc1 = nn.Linear(512, 1024)
    #         self.fc2 = nn.Linear(1024, 256)
    #     def forward(self, x):
    #         return self.fc2(torch.relu(self.fc1(x)))
    #
    # model = DummyModel()
    # quantized_model = apply_dynamic_quantization(model)
    # print(quantized_model)
    pass
'''
        return code

QuantizationProfiler = PrecisionQuantizer