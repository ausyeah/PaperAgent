import pytest
from paperagent.engine.evolutionary_search import EvolutionaryArchitectureSearch
from paperagent.models import EvolutionarySearchResult, CandidateArchitecture

def test_evolutionary_search_deterministic():
    """Test that the evolutionary search is deterministic with the same seed."""
    search_engine1 = EvolutionaryArchitectureSearch(seed=42)
    result1 = search_engine1.search(base_algorithm="Transformer", generations=2, population_size=3)

    search_engine2 = EvolutionaryArchitectureSearch(seed=42)
    result2 = search_engine2.search(base_algorithm="Transformer", generations=2, population_size=3)

    assert result1.best_candidate_id == result2.best_candidate_id
    assert len(result1.candidates) == len(result2.candidates)
    
    for c1, c2 in zip(result1.candidates, result2.candidates):
        assert c1.candidate_id == c2.candidate_id
        assert c1.topology_summary == c2.topology_summary
        assert c1.parameter_count_m == c2.parameter_count_m
        assert c1.simulated_accuracy == c2.simulated_accuracy
        assert c1.latency_ms == c2.latency_ms
        assert c1.pareto_optimal == c2.pareto_optimal

def test_evolutionary_search_generations_population():
    """Test that the search generates the correct number of candidates."""
    search_engine = EvolutionaryArchitectureSearch()
    result = search_engine.search(base_algorithm="ResNet", generations=3, population_size=4)
    
    assert isinstance(result, EvolutionarySearchResult)
    assert result.base_algorithm == "ResNet"
    assert result.generations_evaluated == 3
    assert len(result.candidates) == 12  # 3 * 4
    
    # Check that best candidate is one of the generated ones
    assert result.best_candidate_id in [c.candidate_id for c in result.candidates]
    assert "Evaluated 12 total architectures" in result.evolutionary_insights

def test_evolutionary_search_pareto_frontier():
    """Test that pareto optimal frontier is marked."""
    search_engine = EvolutionaryArchitectureSearch(seed=123)
    result = search_engine.search(base_algorithm="ViT", generations=5, population_size=5)
    
    pareto_candidates = [c for c in result.candidates if c.pareto_optimal]
    assert len(pareto_candidates) > 0  # Should be at least 1 pareto optimal
    
    # Check that best candidate is pareto optimal (if pareto candidates exist)
    best_candidate = next((c for c in result.candidates if c.candidate_id == result.best_candidate_id), None)
    assert best_candidate is not None
    assert best_candidate.pareto_optimal == True

def test_mark_pareto_frontier_logic():
    """Test the core pareto front logic manually."""
    search_engine = EvolutionaryArchitectureSearch()
    candidates = [
        CandidateArchitecture(candidate_id="c1", topology_summary="", parameter_count_m=10, simulated_accuracy=80.0, latency_ms=10.0),
        CandidateArchitecture(candidate_id="c2", topology_summary="", parameter_count_m=10, simulated_accuracy=90.0, latency_ms=10.0), # Dominates c1
        CandidateArchitecture(candidate_id="c3", topology_summary="", parameter_count_m=10, simulated_accuracy=85.0, latency_ms=5.0),  # Non-dominated
        CandidateArchitecture(candidate_id="c4", topology_summary="", parameter_count_m=10, simulated_accuracy=90.0, latency_ms=15.0), # Dominated by c2
    ]
    
    search_engine._mark_pareto_frontier(candidates)
    
    assert candidates[0].pareto_optimal == False # c1
    assert candidates[1].pareto_optimal == True  # c2 (better acc, same lat)
    assert candidates[2].pareto_optimal == True  # c3 (lower acc but lower lat)
    assert candidates[3].pareto_optimal == False # c4 (same acc but higher lat)