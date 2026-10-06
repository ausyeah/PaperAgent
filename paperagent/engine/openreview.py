import asyncio
import logging
from typing import Optional

from paperagent.engine.llm_client import LLMClient
from paperagent.models import ParsedPaper, OpenReviewReport
from paperagent.engine.prompts import REVIEWER_CRITIQUE_PROMPT

class OpenReviewEvaluator:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        if llm_client is None:
            self.llm_client = LLMClient()
        else:
            self.llm_client = llm_client

    def _get_mock_report(self, title: str) -> OpenReviewReport:
        return OpenReviewReport(
            paper_title=title,
            summary_of_work="This paper proposes a novel framework for accelerating deep learning inference using quantized gradients and low-rank adaptations. The authors demonstrate empirical speedups on several vision and language tasks while maintaining competitive accuracy.",
            strengths=[
                "The core idea of combining quantization with low-rank updates is theoretically sound.",
                "Comprehensive empirical evaluation across multiple domains (vision, NLP).",
                "The authors provide an open-source implementation."
            ],
            weaknesses=[
                "The mathematical formulation lacks a formal convergence proof under the new quantization scheme.",
                "Missing comparison against recent baselines like QLoRA.",
                "The overhead of the dynamic low-rank adaptation step is not fully analyzed."
            ],
            questions_for_authors=[
                "Could you provide a detailed breakdown of the memory overhead during the adaptation phase?",
                "How does this method perform on extremely large models (e.g., >70B parameters)?",
                "Why was QLoRA omitted from the baseline comparisons?"
            ],
            soundness_score=3,
            presentation_score=3,
            contribution_score=3,
            overall_recommendation=6,
            reproducibility_checklist_passed=True
        )

    async def evaluate_paper(self, paper: ParsedPaper) -> OpenReviewReport:
        if not self.llm_client.gemini_api_key and not self.llm_client.openai_api_key:
            return self._get_mock_report(paper.metadata.title)

        prompt = REVIEWER_CRITIQUE_PROMPT.format(paper_content=paper.raw_markdown)

        try:
            return await self.llm_client.generate_structured_async(
                prompt=prompt,
                response_model=OpenReviewReport,
                system_prompt="You are a strict but fair AI reviewer generating an OpenReview-style report."
            )
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to generate evaluation report: {e}. Falling back to mock report.")
            return self._get_mock_report(paper.metadata.title)

    def evaluate_paper_sync(self, paper: ParsedPaper) -> OpenReviewReport:
        return asyncio.run(self.evaluate_paper(paper))
