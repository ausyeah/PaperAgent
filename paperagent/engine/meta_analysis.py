from typing import List, Optional

from paperagent.models import PaperProject, MetaAnalysisReport, ConsensusClaim
from paperagent.engine.prompts import META_ANALYSIS_PROMPT
from paperagent.engine.llm_client import LLMClient


class MetaAnalysisEngine:
    """
    Engine for multi-paper meta-analysis and consensus resolution.
    """
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the MetaAnalysisEngine.

        Args:
            llm_client (Optional[LLMClient]): The LLM client to use.
        """
        self.llm_client = llm_client or LLMClient()

    def analyze_multi_paper_consensus(self, topic: str, projects: List[PaperProject], client: Optional[LLMClient] = None) -> MetaAnalysisReport:
        """
        Cross-examines claims and empirical findings across 2 or more paper projects.

        Args:
            topic (str): The specific topic to analyze consensus for.
            projects (List[PaperProject]): A list of 2 or more PaperProject objects.
            client (Optional[LLMClient]): Optionally override the engine's LLM client.

        Returns:
            MetaAnalysisReport: The comprehensive meta-analysis consensus report.
        """
        llm = client or self.llm_client

        if len(projects) < 2:
            raise ValueError("Meta-analysis requires at least 2 papers.")

        # Check if we should fall back to offline mock mode
        if not llm.gemini_api_key and not llm.openai_api_key:
            # Generate a mock response with correct models
            titles = [proj.paper.metadata.title for proj in projects]
            return MetaAnalysisReport(
                topic=topic,
                analyzed_papers=titles,
                claims=[
                    ConsensusClaim(
                        claim=f"Mock claim about {topic}",
                        supporting_papers=[titles[0]],
                        opposing_papers=titles[1:] if len(titles) > 1 else [],
                        consensus_verdict="contested",
                        nuance_analysis="This is a fallback mock nuance analysis."
                    )
                ],
                overall_consensus_summary="This is a fallback mock consensus summary."
            )

        # Build papers_content string
        papers_content = ""
        for i, proj in enumerate(projects):
            title = proj.paper.metadata.title
            abstract = proj.paper.metadata.abstract or "No abstract available."
            # Optionally extract more info if available.
            # But just abstract is often enough for top level summary
            papers_content += f"--- Paper {i+1}: {title} ---\nAbstract: {abstract}\n\n"

        prompt = META_ANALYSIS_PROMPT.format(topic=topic, papers_content=papers_content)

        try:
            return llm.generate_structured(prompt=prompt, response_model=MetaAnalysisReport)
        except Exception as e:
            # Robust fallback on error
            titles = [proj.paper.metadata.title for proj in projects]
            return MetaAnalysisReport(
                topic=topic,
                analyzed_papers=titles,
                claims=[
                    ConsensusClaim(
                        claim=f"Fallback claim due to error: {e}",
                        supporting_papers=[],
                        opposing_papers=[],
                        consensus_verdict="insufficient_evidence",
                        nuance_analysis="Error during LLM generation."
                    )
                ],
                overall_consensus_summary="Error generating summary."
            )


def analyze_multi_paper_consensus(topic: str, projects: List[PaperProject], client: Optional[LLMClient] = None) -> MetaAnalysisReport:
    """Convenience helper to run meta analysis consensus."""
    engine = MetaAnalysisEngine(llm_client=client)
    return engine.analyze_multi_paper_consensus(topic, projects, client)