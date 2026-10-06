"""
PaperAgent AI Reasoning Engine.
"""

from paperagent.engine.analyzer import PaperAnalyzer
from paperagent.engine.comparator import PaperComparator
from paperagent.engine.formula_checker import FormulaDimensionChecker
from paperagent.engine.code_aligner import CodeMathAligner
from paperagent.engine.survey import LiteratureSurveyEngine, synthesize_literature_survey
from paperagent.engine.meta_analysis import MetaAnalysisEngine, analyze_multi_paper_consensus
from paperagent.engine.paper_qa import PaperQAAgent, answer_paper_question
from paperagent.engine.rebuttal import AuthorRebuttalDrafter, draft_author_rebuttal
from paperagent.engine.llm_client import LLMClient
from paperagent.engine.prompts import (
    EXECUTIVE_SUMMARY_PROMPT,
    FORMULA_EXPLAINER_PROMPT,
    REVIEWER_CRITIQUE_PROMPT,
    COMPARATOR_PROMPT,
    CODE_ALIGNER_PROMPT,
    SURVEY_PROMPT,
    META_ANALYSIS_PROMPT,
    PAPER_QA_PROMPT,
    AUTHOR_REBUTTAL_PROMPT,
)
from paperagent.models import ParsedPaper, AnalysisReport

def analyze_paper(paper: ParsedPaper, llm_client: LLMClient = None) -> AnalysisReport:
    """
    Helper function to analyze a paper using the PaperAnalyzer.
    """
    if llm_client is None:
        llm_client = LLMClient()
    analyzer = PaperAnalyzer(llm_client=llm_client)
    return analyzer.analyze(paper)

__all__ = [
    "PaperAnalyzer",
    "PaperComparator",
    "FormulaDimensionChecker",
    "CodeMathAligner",
    "LiteratureSurveyEngine",
    "synthesize_literature_survey",
    "MetaAnalysisEngine",
    "analyze_multi_paper_consensus",
    "PaperQAAgent",
    "answer_paper_question",
    "AuthorRebuttalDrafter",
    "draft_author_rebuttal",
    "analyze_paper",
    "LLMClient",
    "EXECUTIVE_SUMMARY_PROMPT",
    "FORMULA_EXPLAINER_PROMPT",
    "REVIEWER_CRITIQUE_PROMPT",
    "COMPARATOR_PROMPT",
    "CODE_ALIGNER_PROMPT",
    "SURVEY_PROMPT",
    "META_ANALYSIS_PROMPT",
    "PAPER_QA_PROMPT",
    "AUTHOR_REBUTTAL_PROMPT",
]
