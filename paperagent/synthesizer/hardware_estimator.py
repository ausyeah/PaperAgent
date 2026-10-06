from typing import Optional, Dict
import re

from paperagent.models import PaperProject, HardwareProfile

class HardwareEstimator:
    """Hardware Requirements & Hyperparameter Estimator."""

    def __init__(self):
        pass

    def estimate_hardware_profile(self, project: PaperProject, param_count_m: Optional[float] = None) -> HardwareProfile:
        """
        Infers or calculates model parameter count.
        Estimates inference and training VRAM.
        Recommends GPU hardware.
        Generates Optuna hparam tuning code.
        """
        model_name = project.paper.metadata.title

        if param_count_m is None:
            # Try to infer from paper markdown
            param_count_m = self._infer_param_count_from_text(project.paper.raw_markdown)
            if param_count_m is None:
                param_count_m = 100.0 # Default fallback
        
        # Calculate inference VRAM
        vram_inference_mb = self._calculate_inference_vram(param_count_m)

        # Calculate training VRAM
        vram_training_mb = self._calculate_training_vram(param_count_m)

        # Recommend GPU
        recommended_gpu = self._recommend_gpu(vram_training_mb.get('standard_mixed_precision_MB', 0))

        # Generate Optuna code
        optuna_code = self._generate_optuna_code(model_name)

        return HardwareProfile(
            model_name=model_name,
            parameter_count_million=param_count_m,
            vram_inference_mb=vram_inference_mb,
            vram_training_mb=vram_training_mb,
            recommended_gpu=recommended_gpu,
            optuna_hparam_search_code=optuna_code
        )

    def _infer_param_count_from_text(self, text: str) -> Optional[float]:
        """Try to parse parameter count (e.g. 7B, 110M) from markdown."""
        if not text:
            return None
            
        # Very basic regex for common patterns
        b_match = re.search(r'(\d+(?:\.\d+)?)[mMbB]\s*(?:parameters|params)', text, re.IGNORECASE)
        if b_match:
            val = float(b_match.group(1))
            if 'B' in b_match.group(0).upper() or 'b' in b_match.group(0):
                return val * 1000.0
            return val
            
        return None

    def _calculate_inference_vram(self, param_count_m: float) -> Dict[str, float]:
        """
        Estimate inference VRAM (MB) for different sequence lengths.
        Accounts for weight memory (assume FP16 -> 2 bytes per param) and KV cache scaling.
        """
        weight_mem_mb = param_count_m * 2.0  # 2 bytes per param for FP16
        
        # Rough KV cache scaling assumption
        # Let's say basic 1k context uses ~10% of weight memory
        base_kv_mb = max(100.0, weight_mem_mb * 0.1)

        return {
            '1k_ctx': round(weight_mem_mb + base_kv_mb * 1, 2),
            '4k_ctx': round(weight_mem_mb + base_kv_mb * 4, 2),
            '32k_ctx': round(weight_mem_mb + base_kv_mb * 32, 2),
            '128k_ctx': round(weight_mem_mb + base_kv_mb * 128, 2),
        }

    def _calculate_training_vram(self, param_count_m: float) -> Dict[str, float]:
        """
        Estimate training VRAM (MB).
        Assume AdamW optimizer (8 bytes per param).
        Gradients (4 bytes for FP32 or 2 for FP16).
        Activations (scaling roughly with size).
        """
        # Mixed precision (FP16/BF16)
        # Weights: 2 bytes
        # Gradients: 2 bytes
        # Optimizer states (AdamW): 8 bytes (FP32 master weights, momentum, variance)
        model_mem = param_count_m * 2.0
        grad_mem = param_count_m * 2.0
        opt_mem = param_count_m * 8.0
        
        # Activations - rough estimate based on model size
        activation_mem = param_count_m * 4.0

        total_mixed_mb = model_mem + grad_mem + opt_mem + activation_mem

        return {
            'weights_MB': round(model_mem, 2),
            'gradients_MB': round(grad_mem, 2),
            'optimizer_states_MB': round(opt_mem, 2),
            'activations_estimated_MB': round(activation_mem, 2),
            'standard_mixed_precision_MB': round(total_mixed_mb, 2)
        }

    def _recommend_gpu(self, required_mb: float) -> str:
        required_gb = required_mb / 1024.0
        
        if required_gb <= 12:
            return "NVIDIA RTX 4070 (12GB) / RTX 3060"
        elif required_gb <= 24:
            return "NVIDIA RTX 4090 (24GB) / RTX 3090"
        elif required_gb <= 40:
            return "NVIDIA A100 (40GB)"
        elif required_gb <= 80:
            return "NVIDIA A100 (80GB) / H100 (80GB)"
        else:
            return "Multi-H100 Cluster"

    def _generate_optuna_code(self, model_name: str) -> str:
        return f'''import optuna
import torch
import torch.nn as nn
import torch.optim as optim

# Auto-generated Optuna HParam Search for {model_name}

def objective(trial):
    # 1. Suggest Hyperparameters
    lr = trial.suggest_float("lr", 1e-5, 1e-3, log=True)
    batch_size = trial.suggest_categorical("batch_size", [16, 32, 64, 128])
    weight_decay = trial.suggest_float("weight_decay", 1e-6, 1e-2, log=True)
    
    # 2. Build Model & Optimizer (Placeholder)
    # model = MyModel()
    # optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    
    # 3. Training Loop Simulation
    val_loss = 0.0
    for epoch in range(5):
        # train(...)
        # val_loss = validate(...)
        
        # Report intermediate objective value
        trial.report(val_loss, epoch)
        
        # Handle pruning
        if trial.should_prune():
            raise optuna.TrialPruned()
            
    return val_loss

if __name__ == "__main__":
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=20)
    
    print("Best trial:")
    trial = study.best_trial
    print(f"  Value: {{trial.value}}")
    print("  Params: ")
    for key, value in trial.params.items():
        print(f"    {{key}}: {{value}}")
'''


def estimate_hardware_profile(project: PaperProject, param_count_m: Optional[float] = None) -> HardwareProfile:
    """Convenience helper function to estimate hardware profile."""
    estimator = HardwareEstimator()
    return estimator.estimate_hardware_profile(project, param_count_m)