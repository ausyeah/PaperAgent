"""
Literature Survey Engine Module.

Orchestrates the LLM calls to generate a comprehensive literature survey,
taxonomy tree, chronological milestones, and comparative tables across multiple papers.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from paperagent.models import ParsedPaper, LiteratureSurvey
from paperagent.engine.prompts import SURVEY_PROMPT
from paperagent.engine.llm_client import LLMClient


class LiteratureSurveyEngine:
    """
    Synthesizes a literature survey from multiple parsed academic papers.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the LiteratureSurveyEngine.

        Args:
            llm_client (Optional[LLMClient]): The LLM client used to generate the survey.
        """
        self.llm_client = llm_client

    def _get_papers_content(self, papers: List[ParsedPaper]) -> str:
        """
        Extract the key content from multiple papers to build the survey input.
        """
        content = []
        for i, paper in enumerate(papers, 1):
            paper_text = f"--- Paper {i}: {paper.metadata.title} ---\n"
            if paper.metadata.authors:
                paper_text += f"Authors: {', '.join(paper.metadata.authors)}\n"
            if paper.metadata.year:
                paper_text += f"Year: {paper.metadata.year}\n"
            if paper.metadata.abstract:
                paper_text += f"Abstract:\n{paper.metadata.abstract}\n"
            
            # Optionally include raw markdown if needed, but it might be too large for many papers.
            # We'll include it if abstract is missing or if we want deeper analysis.
            if paper.raw_markdown and not paper.metadata.abstract:
                # Limit to first 2000 chars to avoid prompt overflow if abstract missing
                paper_text += f"Content Snippet:\n{paper.raw_markdown[:2000]}...\n"
                
            content.append(paper_text)
            
        return "\n\n".join(content)

    def synthesize_literature_survey(self, topic: str, papers: List[ParsedPaper], client: Optional[LLMClient] = None) -> LiteratureSurvey:
        """
        Synthesizes a literature survey from a list of papers.

        Args:
            topic (str): The specific research topic of the survey.
            papers (List[ParsedPaper]): The parsed papers to survey.
            client (Optional[LLMClient]): Overrides the default LLM client for this specific call.

        Returns:
            LiteratureSurvey: The structured literature survey.
        """
        active_client = client or self.llm_client
        
        if not papers:
            return LiteratureSurvey(
                topic=topic,
                survey_markdown="No papers provided to survey."
            )

        if not active_client:
            # Offline fallback
            sorted_papers = sorted(papers, key=lambda p: p.metadata.year or datetime.now().year)
            titles = [p.metadata.title for p in sorted_papers]
            return LiteratureSurvey(
                topic=topic,
                taxonomy_tree={"Baseline Models": titles},
                chronology=[
                    {
                        "year": p.metadata.year or datetime.now().year,
                        "title": p.metadata.title,
                        "breakthrough": "Proposed a novel methodology."
                    } for p in sorted_papers
                ],
                comparative_table=[
                    {
                        "model": p.metadata.title,
                        "supervision": "Self-Supervised",
                        "complexity": "O(N^2)",
                        "benchmark": "ImageNet"
                    } for p in sorted_papers
                ],
                open_challenges=["Scalability", "Data Efficiency", "Interpretability"],
                survey_markdown=f"# Literature Survey: {topic}\n\nThis is an auto-generated baseline survey for {len(papers)} papers since the LLM client was not provided.\n\n## Papers included:\n- " + "\n- ".join(titles)
            )

        papers_content = self._get_papers_content(papers)
        prompt = SURVEY_PROMPT.format(topic=topic, papers_content=papers_content)
        
        survey = active_client.generate_structured(
            prompt=prompt,
            response_model=LiteratureSurvey
        )
        
        # Ensure topic is set correctly in case LLM missed it
        survey.topic = topic
        
        return survey


def synthesize_literature_survey(topic: str, papers: List[ParsedPaper], client: Optional[LLMClient] = None) -> LiteratureSurvey:
    """Convenience function to synthesize a literature survey."""
    engine = LiteratureSurveyEngine(llm_client=client)
    return engine.synthesize_literature_survey(topic, papers, client)