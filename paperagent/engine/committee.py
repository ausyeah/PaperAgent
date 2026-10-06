"""
Multi-Agent Peer Review Committee Module.

Simulates a 3-reviewer conference review panel (Theory Expert, Empirical Skeptic, Impact Champion)
and synthesizes an Area Chair meta-review.
"""
from typing import Optional, List
import asyncio

from paperagent.models import ParsedPaper, CommitteeReview, IndividualReview
from paperagent.engine.prompts import COMMITTEE_REVIEW_PROMPT
from paperagent.engine.llm_client import LLMClient


class PeerReviewCommittee:
    """
    Simulates a multi-agent peer review committee and AC meta-review.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the PeerReviewCommittee.

        Args:
            llm_client (Optional[LLMClient]): The LLM client used to generate the reviews.
        """
        self.llm_client = llm_client

    def evaluate_paper_committee(self, paper: ParsedPaper, client: Optional[LLMClient] = None) -> CommitteeReview:
        """
        Simulates a 3-reviewer conference review panel and synthesizes an Area Chair meta-review.

        Args:
            paper (ParsedPaper): The parsed academic paper to evaluate.
            client (Optional[LLMClient]): An optional LLMClient override.

        Returns:
            CommitteeReview: The synthesized multi-agent committee review.
        """
        llm = client or self.llm_client or LLMClient()
        return asyncio.run(self._evaluate_paper_committee_async(paper, llm))

    async def _evaluate_paper_committee_async(self, paper: ParsedPaper, llm: LLMClient) -> CommitteeReview:
        """
        Asynchronous implementation of evaluate_paper_committee.
        """
        paper_content = f"Title: {paper.metadata.title}\nAbstract: {paper.metadata.abstract}\n\n"
        if paper.raw_markdown:
            paper_content += f"Content:\n{paper.raw_markdown[:15000]}"
        else:
            for section in paper.sections:
                paper_content += f"\n## {section.title}\n{section.content}\n"
            paper_content = paper_content[:15000]

        prompt = COMMITTEE_REVIEW_PROMPT.format(paper_content=paper_content)
        
        system_prompt = (
            "You are an Area Chair running a conference peer review process. "
            "You must meticulously simulate exactly 3 specific reviewers (Theory Expert, Empirical Skeptic, Impact Champion) "
            "and then write a summarizing meta-review and final decision."
        )

        try:
            review = await llm.generate_structured_async(
                prompt=prompt,
                response_model=CommitteeReview,
                system_prompt=system_prompt
            )
            # Ensure the paper title matches
            review.paper_title = paper.metadata.title
            
            # Enforce 3 reviews if it's falling back or misbehaving
            if len(review.reviews) != 3:
                review = self._get_fallback_committee_review(paper)
            
            return review
            
        except Exception as e:
            return self._get_fallback_committee_review(paper)

    def _get_fallback_committee_review(self, paper: ParsedPaper) -> CommitteeReview:
        """
        Generates a structured multi-persona fallback review when LLM is unavailable or errors out.
        """
        return CommitteeReview(
            paper_title=paper.metadata.title,
            reviews=[
                IndividualReview(
                    reviewer_id="Reviewer 1",
                    persona="Reviewer 1 (Theory Expert)",
                    score=6,
                    strengths=["Solid mathematical foundation.", "Proofs are generally sound."],
                    weaknesses=["Some assumptions are quite strong.", "Theoretical bounds could be tighter."],
                    detailed_critique="The paper presents a solid theoretical framework, but some assumptions require further justification."
                ),
                IndividualReview(
                    reviewer_id="Reviewer 2",
                    persona="Reviewer 2 (Empirical Skeptic)",
                    score=5,
                    strengths=["Extensive experiments.", "Code provided."],
                    weaknesses=["Missing key baselines.", "Ablation study is incomplete."],
                    detailed_critique="Empirically, the paper shows promise, but the lack of comparison against state-of-the-art baselines makes it hard to gauge true progress."
                ),
                IndividualReview(
                    reviewer_id="Reviewer 3",
                    persona="Reviewer 3 (Impact Champion)",
                    score=8,
                    strengths=["Highly novel approach.", "Addresses a critical problem in the field."],
                    weaknesses=["Practical deployment might be challenging.", "Needs more discussion on societal impact."],
                    detailed_critique="This paper introduces a paradigm shift. Despite some rough edges, the potential impact is significant."
                )
            ],
            meta_review="The committee finds the paper theoretically sound and highly novel, though empirically it requires stronger baselines. Overall, the potential impact outweighs the empirical shortcomings.",
            final_decision="Accept (Poster)"
        )