"""
Automated Scientific Hypothesis Generator module.
"""
from typing import Optional
import logging
import uuid

from paperagent.models import ParsedPaper, HypothesisCollection, ResearchHypothesis
from paperagent.engine.llm_client import LLMClient
from paperagent.engine.prompts import HYPOTHESIS_GENERATOR_PROMPT

logger = logging.getLogger(__name__)

class ScientificHypothesisGenerator:
    """Generates concrete algorithmic mutations and research hypotheses from parsed papers."""

    def generate_hypotheses(
        self,
        paper: ParsedPaper,
        client: Optional[LLMClient] = None
    ) -> HypothesisCollection:
        """
        Analyzes paper limitations, mathematical formulations, and empirical baselines to
        generate 3-5 concrete algorithmic mutations/hypotheses.
        """
        if client is None:
            client = LLMClient()
            
        paper_content = f"Title: {paper.metadata.title}\n"
        paper_content += f"Abstract: {paper.metadata.abstract}\n"
        # Include some sections text for context if available
        if paper.sections:
            for i, section in enumerate(paper.sections[:3]):
                paper_content += f"\nSection {section.title}:\n{section.content[:1000]}...\n"

        prompt = HYPOTHESIS_GENERATOR_PROMPT.format(paper_content=paper_content)
        
        try:
            collection = client.generate_structured(
                prompt=prompt,
                response_model=HypothesisCollection,
                system_prompt="You are an expert AI research scientist."
            )
            # Ensure the title matches if LLM gets confused
            collection.paper_title = paper.metadata.title
            
            # Ensure feasibility scores are valid
            for hyp in collection.hypotheses:
                if not 0.0 <= hyp.feasibility_score <= 1.0:
                    hyp.feasibility_score = max(0.0, min(1.0, hyp.feasibility_score))
                    
            if not collection.hypotheses:
                return self._get_offline_fallback(paper)

            return collection
            
        except Exception as e:
            logger.error(f"Failed to generate hypotheses using LLM: {e}. Returning offline fallback.")
            return self._get_offline_fallback(paper)

    def _get_offline_fallback(self, paper: ParsedPaper) -> HypothesisCollection:
        """Deterministic offline heuristic fallback when LLM is unavailable."""
        hypotheses = [
            ResearchHypothesis(
                hypothesis_id=f"hyp-{uuid.uuid4().hex[:6]}",
                title="Adaptive Skip Connections",
                rationale="The current architecture relies on static skip connections which may limit representational flexibility across varying data distributions.",
                proposed_modification="Introduce learnable gating mechanisms (e.g., sigmoid multipliers) to all residual blocks to dynamically scale the skip connection contribution.",
                expected_gain="Improved convergence speed and potentially better generalization on complex datasets.",
                feasibility_score=0.85,
                validation_protocol="Train baseline and modified models on standard benchmarks; compare loss curves and final evaluation metrics."
            ),
            ResearchHypothesis(
                hypothesis_id=f"hyp-{uuid.uuid4().hex[:6]}",
                title="Linear Attention Substitution",
                rationale="Standard self-attention scales quadratically with sequence length, causing memory bottlenecks for long contexts.",
                proposed_modification="Replace exact softmax attention with a kernelized linear attention variant or Performer-style approximation.",
                expected_gain="O(N) memory complexity allowing 4x longer context windows with minimal performance degradation.",
                feasibility_score=0.75,
                validation_protocol="Profile peak memory usage across sequence lengths; measure perplexity trade-off on long-document validation sets."
            ),
            ResearchHypothesis(
                hypothesis_id=f"hyp-{uuid.uuid4().hex[:6]}",
                title="RMSNorm instead of LayerNorm",
                rationale="LayerNorm computes both mean and variance, which adds computational overhead without strictly necessary empirical benefits for all architectures.",
                proposed_modification="Swap all LayerNorm modules for Root Mean Square Normalization (RMSNorm) to eliminate the mean-centering operation.",
                expected_gain="10-15% speedup in forward/backward pass throughput on GPU with identical convergence properties.",
                feasibility_score=0.95,
                validation_protocol="Benchmark throughput (samples/sec) on identical hardware; verify that zero-shot task performance remains within error margins."
            )
        ]
        
        return HypothesisCollection(
            paper_title=paper.metadata.title,
            hypotheses=hypotheses,
            strategic_summary="Generated heuristic architectural mutations focusing on parameter efficiency, memory scaling, and computational throughput."
        )

def generate_hypotheses(paper: ParsedPaper, client: Optional[LLMClient] = None) -> HypothesisCollection:
    """Convenience helper function."""
    generator = ScientificHypothesisGenerator()
    return generator.generate_hypotheses(paper, client)