import pytest
from paperagent.runner.experiment_runner import ExperimentMatrixRunner
from paperagent.models import ExperimentMatrixResult

def test_experiment_matrix_runner_basic():
    runner = ExperimentMatrixRunner()
    hparam_grid = {
        "lr": [1e-3, 1e-4],
        "batch_size": [32, 64]
    }
    seeds = [42, 123]
    result = runner.run_matrix("TransformerLRGrid", hparam_grid, seeds)

    assert isinstance(result, ExperimentMatrixResult)
    assert result.matrix_name == "TransformerLRGrid"
    # 2 lrs * 2 batch_sizes * 2 seeds = 8 runs
    assert result.total_runs == 8
    assert len(result.runs) == 8
    assert result.best_run_id != ""
    assert "mean" in result.aggregate_statistics
    assert "std" in result.aggregate_statistics
    assert "min" in result.aggregate_statistics
    assert "max" in result.aggregate_statistics
    assert result.aggregate_statistics["max"] >= result.aggregate_statistics["min"]
    assert "Experiment Matrix Summary: TransformerLRGrid" in result.ascii_summary

def test_experiment_matrix_runner_empty():
    runner = ExperimentMatrixRunner()
    result = runner.run_matrix("EmptyMatrix", {}, seeds=[42])
    assert result.total_runs == 1
    assert result.best_run_id != ""
