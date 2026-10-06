"""
Reproducibility Evaluator module.
"""
import re
from typing import Optional
from paperagent.models import ParsedPaper, ReproducibilityScorecard
from paperagent.engine.llm_client import LLMClient
from paperagent.engine.prompts import REPRODUCIBILITY_SCORECARD_PROMPT
import logging

logger = logging.getLogger(__name__)

class ReproducibilityEvaluator:
    """Evaluates the empirical reproducibility of academic papers."""

    def evaluate_reproducibility(
        self,
        paper: ParsedPaper,
        client: Optional[LLMClient] = None
    ) -> ReproducibilityScorecard:
        """
        Evaluates a paper against 10 reproducibility criteria using an LLM,
        falling back to regex heuristics if the LLM is unavailable.
        """
        if client is None:
            client = LLMClient()
            
        paper_text = paper.raw_markdown if paper.raw_markdown else ""
        if not paper_text and paper.sections:
            paper_text = "\n".join([s.content for s in paper.sections])

        prompt = REPRODUCIBILITY_SCORECARD_PROMPT.format(paper_content=paper_text)
        
        try:
            scorecard = client.generate_structured(
                prompt=prompt,
                response_model=ReproducibilityScorecard,
                system_prompt="You are an expert AI researcher evaluating paper reproducibility."
            )
            # Ensure paper title is populated correctly
            scorecard.paper_title = paper.metadata.title
            return scorecard
        except Exception as e:
            logger.error(f"LLM reproducibility evaluation failed: {e}. Using offline fallback.")
            return self._evaluate_offline(paper, paper_text)

    def _evaluate_offline(self, paper: ParsedPaper, text: str) -> ReproducibilityScorecard:
        """Offline regex/heuristic fallback for reproducibility evaluation."""
        text_lower = text.lower()
        
        criteria_checks = {
            "Code Repository URL Provided": bool(re.search(r'github\.com|gitlab\.com', text_lower)),
            "Dataset Availability & Licensing": bool(re.search(r'dataset|license|mit|gpl', text_lower)),
            "Hyperparameter Specification": bool(re.search(r'learning rate|batch size|epochs|lr=', text_lower)),
            "Hardware Environment Specified": bool(re.search(r'gpu|nvidia|a100|v100|tpu', text_lower)),
            "Random Seed Reporting & Multiple Runs": bool(re.search(r'seed|random state|multiple runs', text_lower)),
            "Error Bars / Standard Deviations Reported": bool(re.search(r'error bar|standard deviation|std|\+/-|\\pm', text_lower)),
            "Compute Budget / Training Time Disclosed": bool(re.search(r'training time|compute budget|hours|days|compute', text_lower)),
            "Evaluation Protocol Consistency": bool(re.search(r'baseline|protocol|fair comparison', text_lower)),
            "Model Checkpoint Download Links": bool(re.search(r'huggingface\.co|checkpoint|weights|zenodo', text_lower)),
            "Proof / Derivation Steps Clear": bool(re.search(r'proof|derivation|lemma|theorem', text_lower))
        }

        score = sum(10 for passed in criteria_checks.values() if passed)
        
        if score >= 80:
            verdict = "High Reproducibility"
        elif score >= 50:
            verdict = "Moderate Reproducibility"
        else:
            verdict = "Low Reproducibility"
            
        recommendations = []
        if not criteria_checks["Code Repository URL Provided"]:
            recommendations.append("Release source code repository (e.g., GitHub) for the implementation.")
        if not criteria_checks["Dataset Availability & Licensing"]:
            recommendations.append("Provide details on dataset availability and licensing terms.")
        if not criteria_checks["Hyperparameter Specification"]:
            recommendations.append("Explicitly document all hyperparameters including learning rate, batch size, etc.")
        if not criteria_checks["Hardware Environment Specified"]:
            recommendations.append("Specify hardware details such as GPU type and count used for experiments.")
        if not criteria_checks["Random Seed Reporting & Multiple Runs"]:
            recommendations.append("Report random seeds and average results over multiple runs.")
        if not criteria_checks["Error Bars / Standard Deviations Reported"]:
            recommendations.append("Include standard deviations or error bars in empirical results.")
        if not criteria_checks["Compute Budget / Training Time Disclosed"]:
            recommendations.append("Disclose total compute budget or training time.")
        if not criteria_checks["Evaluation Protocol Consistency"]:
            recommendations.append("Clarify evaluation protocols to ensure fair baseline comparisons.")
        if not criteria_checks["Model Checkpoint Download Links"]:
            recommendations.append("Provide public links to download pre-trained model checkpoints.")
        if not criteria_checks["Proof / Derivation Steps Clear"]:
            recommendations.append("Provide explicit step-by-step mathematical proofs or derivations.")

        return ReproducibilityScorecard(
            paper_title=paper.metadata.title,
            score=score,
            criteria_checklist=criteria_checks,
            verdict_level=verdict,
            improvement_recommendations=recommendations
        )

def evaluate_reproducibility(paper: ParsedPaper, client: Optional[LLMClient] = None) -> ReproducibilityScorecard:
    """Helper function to evaluate reproducibility."""
    evaluator = ReproducibilityEvaluator()
    return evaluator.evaluate_reproducibility(paper, client)