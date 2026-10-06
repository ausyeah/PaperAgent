"""
PaperAgent AI Reasoning Engine.
"""

from paperagent.engine.analyzer import PaperAnalyzer
from paperagent.engine.comparator import PaperComparator
from paperagent.engine.prompts import (
    EXECUTIVE_SUMMARY_PROMPT,
    FORMULA_EXPLAINER_PROMPT,
    REVIEWER_CRITIQUE_PROMPT,
    COMPARATOR_PROMPT,
    CODE_ALIGNER_PROMPT
)
from paperagent.engine.llm_client import LLMClient
from paperagent.models import ParsedPaper, AnalysisReport

def analyze_paper(paper: ParsedPaper, llm_client: LLMClient = None) -> AnalysisReport:
    """
    Helper function to analyze a paper using the PaperAnalyzer.

    Args:
        paper (ParsedPaper): The parsed paper to analyze.
        llm_client (LLMClient, optional): The LLM client to use. Defaults to a new LLMClient.

    Returns:
        AnalysisReport: The comprehensive analysis report.
    """
    if llm_client is None:
        llm_client = LLMClient()
    analyzer = PaperAnalyzer(llm_client=llm_client)
    return analyzer.analyze(paper)

__all__ = [
    "PaperAnalyzer",
    "PaperComparator",
    "analyze_paper",
    "EXECUTIVE_SUMMARY_PROMPT",
    "FORMULA_EXPLAINER_PROMPT",
    "REVIEWER_CRITIQUE_PROMPT",
    "COMPARATOR_PROMPT",
    "CODE_ALIGNER_PROMPT",
    "LLMClient"
]
