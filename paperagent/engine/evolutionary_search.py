import random
from typing import List, Dict, Any
from paperagent.models import EvolutionarySearchResult, CandidateArchitecture

class EvolutionaryArchitectureSearch:
    """Evolutionary Neural Architecture Search Engine."""

    def __init__(self, seed: int = 42):
        """
        Initializes the evolutionary search engine.
        
        Args:
            seed (int): Random seed for reproducible deterministic execution.
        """
        self.seed = seed
        self.random = random.Random(seed)

    def _generate_candidate(self, candidate_id: str, base_algorithm: str) -> CandidateArchitecture:
        """Generates a random candidate architecture based on the base algorithm."""
        # Evolve architecture topology variations
        layer_depth = self.random.randint(2, 24)
        attention_heads = self.random.choice([4, 8, 12, 16])
        expansion_ratio = self.random.choice([2, 4, 8])
        activation = self.random.choice(["ReLU", "GELU", "Swish", "SiLU"])

        topology_summary = (
            f"Depth={layer_depth}, Heads={attention_heads}, "
            f"ExpRatio={expansion_ratio}, Act={activation}"
        )

        # Simulate metrics based on random evolution
        # Parameter count: generally goes up with depth, heads, exp_ratio
        parameter_count_m = (layer_depth * attention_heads * expansion_ratio) / 10.0 + self.random.uniform(10.0, 50.0)
        
        # Accuracy: generally goes up with parameters but with diminishing returns and noise
        simulated_accuracy = min(99.0, 60.0 + (parameter_count_m / 10.0) + self.random.uniform(-5.0, 5.0))
        
        # Latency: generally goes up with parameter count
        latency_ms = parameter_count_m * 0.5 + self.random.uniform(5.0, 15.0)

        return CandidateArchitecture(
            candidate_id=candidate_id,
            topology_summary=topology_summary,
            parameter_count_m=round(parameter_count_m, 2),
            simulated_accuracy=round(simulated_accuracy, 2),
            latency_ms=round(latency_ms, 2),
            pareto_optimal=False
        )

    def _mark_pareto_frontier(self, candidates: List[CandidateArchitecture]) -> None:
        """
        Identifies and marks Pareto-optimal candidates.
        We want to maximize simulated_accuracy and minimize latency_ms.
        """
        for c1 in candidates:
            is_pareto = True
            for c2 in candidates:
                if c1 == c2:
                    continue
                
                # c2 dominates c1 if it is strictly better or equal in all objectives 
                # and strictly better in at least one objective.
                better_or_equal_acc = c2.simulated_accuracy >= c1.simulated_accuracy
                better_or_equal_lat = c2.latency_ms <= c1.latency_ms
                
                better_acc = c2.simulated_accuracy > c1.simulated_accuracy
                better_lat = c2.latency_ms < c1.latency_ms
                
                if better_or_equal_acc and better_or_equal_lat and (better_acc or better_lat):
                    is_pareto = False
                    break
            c1.pareto_optimal = is_pareto

    def search(
        self, base_algorithm: str, generations: int = 5, population_size: int = 6
    ) -> EvolutionarySearchResult:
        """
        Evolves architecture topology variations and evaluates fitness.
        
        Args:
            base_algorithm (str): The base algorithm to evolve from.
            generations (int): Number of evolutionary generations.
            population_size (int): Number of candidates per generation.
            
        Returns:
            EvolutionarySearchResult: Result of the evolutionary search.
        """
        all_candidates = []
        
        # Reset random seed for deterministic execution each search
        self.random.seed(self.seed)

        for gen in range(generations):
            for pop in range(population_size):
                candidate_id = f"gen{gen}_pop{pop}_{self.random.randint(1000, 9999)}"
                candidate = self._generate_candidate(candidate_id, base_algorithm)
                all_candidates.append(candidate)
                
        # Identify pareto-optimal
        self._mark_pareto_frontier(all_candidates)
        
        # Select best candidate (e.g., highest accuracy among pareto optimal)
        pareto_candidates = [c for c in all_candidates if c.pareto_optimal]
        
        if pareto_candidates:
            best_candidate = max(pareto_candidates, key=lambda c: c.simulated_accuracy)
        else:
            best_candidate = max(all_candidates, key=lambda c: c.simulated_accuracy)

        best_id = best_candidate.candidate_id
        
        insights = (
            f"Evaluated {generations * population_size} total architectures over {generations} generations. "
            f"Identified {len(pareto_candidates)} Pareto-optimal architectures balancing accuracy vs latency trade-offs. "
            f"Best candidate {best_id} achieved {best_candidate.simulated_accuracy}% accuracy at {best_candidate.latency_ms}ms latency."
        )

        return EvolutionarySearchResult(
            base_algorithm=base_algorithm,
            generations_evaluated=generations,
            candidates=all_candidates,
            best_candidate_id=best_id,
            evolutionary_insights=insights
        )