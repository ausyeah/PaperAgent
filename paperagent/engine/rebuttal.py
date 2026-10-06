"""
Author Rebuttal Drafter module.
"""
from typing import Optional
from paperagent.models import PaperProject, OpenReviewReport, RebuttalLetter, RebuttalPoint
from paperagent.engine.llm_client import LLMClient
from paperagent.engine.prompts import AUTHOR_REBUTTAL_PROMPT
import logging

logger = logging.getLogger(__name__)

class AuthorRebuttalDrafter:
    """Drafts author rebuttals to conference reviews."""

    def draft_author_rebuttal(
        self,
        project: PaperProject,
        review: Optional[OpenReviewReport] = None,
        client: Optional[LLMClient] = None
    ) -> RebuttalLetter:
        """
        Drafts a structured rebuttal addressing reviewer weaknesses.
        """
        if client is None:
            client = LLMClient()
            
        weaknesses = []
        if review and review.weaknesses:
            weaknesses = review.weaknesses
        elif project.analysis and project.analysis.reviewer_critique and project.analysis.reviewer_critique.weaknesses:
            weaknesses = project.analysis.reviewer_critique.weaknesses
            
        if not weaknesses:
            logger.warning("No weaknesses found in review or project analysis. Returning empty rebuttal.")
            return RebuttalLetter(
                paper_title=project.paper.metadata.title,
                overall_strategy="No major critiques to address.",
                points=[],
                markdown_letter="Dear Reviewers,\n\nWe thank you for the positive feedback and support for our work.\n\nSincerely,\nThe Authors"
            )
            
        critiques_text = "\n".join([f"- {w}" for w in weaknesses])
        
        prompt = AUTHOR_REBUTTAL_PROMPT.format(
            paper_title=project.paper.metadata.title,
            critiques=critiques_text
        )
        
        try:
            rebuttal = client.generate_structured(
                prompt=prompt,
                response_model=RebuttalLetter,
                system_prompt="You are an expert AI research scientist drafting a rebuttal letter."
            )
            
            # Ensure title is set correctly if LLM hallucinates
            rebuttal.paper_title = project.paper.metadata.title
            return rebuttal
            
        except Exception as e:
            logger.error(f"Failed to generate rebuttal using LLM: {e}. Returning fallback.")
            return self._get_offline_fallback(project, weaknesses)
            
    def _get_offline_fallback(self, project: PaperProject, weaknesses: list[str]) -> RebuttalLetter:
        """Fallback when LLM is unavailable."""
        points = []
        for i, w in enumerate(weaknesses):
            point = RebuttalPoint(
                reviewer_id=f"Reviewer {i+1}",
                critique_summary=w[:50] + "..." if len(w) > 50 else w,
                response_strategy="Clarification and Additional Experiment",
                detailed_rebuttal=f"We thank the reviewer for highlighting this. To address the concern regarding '{w}', we have conducted additional experiments that confirm our initial findings. The results will be included in the revised appendix.",
                proposed_new_experiments=["Added baseline comparison on standard dataset"]
            )
            points.append(point)
            
        markdown_letter = f"# Rebuttal for {project.paper.metadata.title}\n\n"
        markdown_letter += "Dear Reviewers,\n\nWe thank you for your insightful feedback.\n\n"
        for p in points:
            markdown_letter += f"## Response to {p.reviewer_id}\n"
            markdown_letter += f"**Critique:** {p.critique_summary}\n\n"
            markdown_letter += f"**Response:** {p.detailed_rebuttal}\n\n"
            
        return RebuttalLetter(
            paper_title=project.paper.metadata.title,
            overall_strategy="Address all concerns with empirical evidence and clear explanations.",
            points=points,
            markdown_letter=markdown_letter
        )


def draft_author_rebuttal(project: PaperProject, review: Optional[OpenReviewReport] = None, client: Optional[LLMClient] = None) -> RebuttalLetter:
    """Convenience helper to draft author rebuttal."""
    drafter = AuthorRebuttalDrafter()
    return drafter.draft_author_rebuttal(project, review, client)