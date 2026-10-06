import itertools
import random
import uuid
import math
from typing import Dict, List, Any
from paperagent.models import ExperimentRunRecord, ExperimentMatrixResult

class ExperimentMatrixRunner:
    def run_matrix(
        self, 
        matrix_name: str, 
        hparam_grid: Dict[str, List[Any]], 
        seeds: List[int] = None
    ) -> ExperimentMatrixResult:
        if seeds is None:
            seeds = [42, 123]
            
        keys = list(hparam_grid.keys())
        values = list(hparam_grid.values())
        
        runs: List[ExperimentRunRecord] = []
        
        if not values:
            combinations = [{}]
        else:
            combinations = list(itertools.product(*values))
        
        for idx, combo in enumerate(combinations):
            if keys:
                hparams = dict(zip(keys, combo))
            else:
                hparams = {}
            for seed in seeds:
                # Deterministic metric simulation
                hparam_str = str(sorted(hparams.items()))
                rng = random.Random(f"{seed}_{hparam_str}")
                
                final_metric = rng.uniform(0.5, 0.99)
                duration_seconds = rng.uniform(10.0, 3600.0)
                
                # generate run_id deterministically for the same seed and hparams
                run_id = str(uuid.UUID(int=rng.getrandbits(128), version=4))
                
                record = ExperimentRunRecord(
                    run_id=run_id,
                    seed=seed,
                    hyperparameters=hparams,
                    final_metric=final_metric,
                    duration_seconds=duration_seconds,
                    status="COMPLETED"
                )
                runs.append(record)
                
        # Aggregate statistics
        if not runs:
            return ExperimentMatrixResult(
                matrix_name=matrix_name,
                total_runs=0,
                runs=[],
                best_run_id="",
                aggregate_statistics={"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0},
                ascii_summary="No runs executed."
            )
            
        metrics = [r.final_metric for r in runs]
        mean_metric = sum(metrics) / len(metrics)
        if len(metrics) > 1:
            std_metric = math.sqrt(sum((m - mean_metric) ** 2 for m in metrics) / (len(metrics) - 1))
        else:
            std_metric = 0.0
            
        min_metric = min(metrics)
        max_metric = max(metrics)
        
        aggregate_statistics = {
            "mean": mean_metric,
            "std": std_metric,
            "min": min_metric,
            "max": max_metric
        }
        
        best_run = max(runs, key=lambda r: r.final_metric)
        
        lines = []
        lines.append("-" * 60)
        lines.append(f"Experiment Matrix Summary: {matrix_name}")
        lines.append("-" * 60)
        lines.append(f"Total Runs: {len(runs)}")
        lines.append(f"Best Metric: {best_run.final_metric:.4f} (Run: {best_run.run_id})")
        lines.append("-" * 60)
        lines.append(f"Mean: {mean_metric:.4f} | Std: {std_metric:.4f} | Min: {min_metric:.4f} | Max: {max_metric:.4f}")
        lines.append("-" * 60)
        
        ascii_summary = "\n".join(lines)
        
        return ExperimentMatrixResult(
            matrix_name=matrix_name,
            total_runs=len(runs),
            runs=runs,
            best_run_id=best_run.run_id,
            aggregate_statistics=aggregate_statistics,
            ascii_summary=ascii_summary
        )