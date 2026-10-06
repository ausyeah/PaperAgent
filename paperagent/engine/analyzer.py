"""
Paper Analyzer Module.

Orchestrates the LLM calls to generate comprehensive paper analysis,
formula explanations, and peer-reviewer critiques.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from paperagent.models import (
    ParsedPaper,
    AnalysisReport,
    FormulaExplanation,
    ReviewerCritique,
    ExtractedFormula
)
from paperagent.engine.prompts import (
    EXECUTIVE_SUMMARY_PROMPT,
    FORMULA_EXPLAINER_PROMPT,
    REVIEWER_CRITIQUE_PROMPT
)
from paperagent.engine.llm_client import LLMClient


class ExecutiveSummaryResult(BaseModel):
    """Temporary model to parse the executive summary response."""
    executive_summary: str = Field(default="")
    core_problem: str = Field(default="")
    key_innovation: str = Field(default="")
    methodology_overview: str = Field(default="")


class PaperAnalyzer:
    """
    Analyzes parsed academic papers using LLMs.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the PaperAnalyzer.

        Args:
            llm_client (LLMClient): The LLM client used to generate analysis.
        """
        self.llm_client = llm_client

    def _get_full_text(self, paper: ParsedPaper) -> str:
        """
        Extract the full text from the paper sections if raw_markdown is empty.
        """
        if paper.raw_markdown:
            return paper.raw_markdown

        content = []
        content.append(f"# {paper.metadata.title}")
        if paper.metadata.abstract:
            content.append(f"## Abstract\n{paper.metadata.abstract}")

        for section in paper.sections:
            content.append(f"{'#' * (section.level + 1)} {section.title}\n{section.content}")

        return "\n\n".join(content)

    def analyze(self, paper: ParsedPaper) -> AnalysisReport:
        """
        Analyzes a parsed paper and returns an AnalysisReport.

        Args:
            paper (ParsedPaper): The parsed paper object to analyze.

        Returns:
            AnalysisReport: The comprehensive analysis report.
        """
        paper_content = self._get_full_text(paper)
        if not paper_content.strip():
            # Graceful handling for completely empty papers
            paper_content = "This paper has no extractable content."

        # 1. Generate Executive Summary and Core Insights
        summary_prompt = EXECUTIVE_SUMMARY_PROMPT.format(paper_content=paper_content)
        summary_result = self.llm_client.generate_structured(
            prompt=summary_prompt,
            response_model=ExecutiveSummaryResult
        )

        # 2. Extract and Explain Top 5 Formulas
        formula_explanations: List[FormulaExplanation] = []
        all_formulas: List[ExtractedFormula] = []
        for section in paper.sections:
            all_formulas.extend(section.formulas)

        # Grab up to the first 5 formulas
        top_formulas = all_formulas[:5]

        for formula in top_formulas:
            formula_prompt = FORMULA_EXPLAINER_PROMPT.format(
                latex=formula.latex,
                context=formula.context_text or "No specific context provided."
            )
            try:
                # We need an intermediary model without the `formula_id` and `latex` to parse just the LLM output
                # since the prompt only asks for glossary, intuition, and breakdown.
                class PartialFormulaExpl(BaseModel):
                    variable_glossary: Dict[str, str] = Field(default_factory=dict)
                    intuitive_intuition: str = Field(default="")
                    step_by_step_breakdown: List[str] = Field(default_factory=list)

                expl_result = self.llm_client.generate_structured(
                    prompt=formula_prompt,
                    response_model=PartialFormulaExpl
                )

                formula_explanations.append(
                    FormulaExplanation(
                        formula_id=formula.id,
                        latex=formula.latex,
                        variable_glossary=expl_result.variable_glossary,
                        intuitive_intuition=expl_result.intuitive_intuition,
                        step_by_step_breakdown=expl_result.step_by_step_breakdown
                    )
                )
            except Exception as e:
                # Graceful handling if formula explanation fails
                print(f"Warning: Failed to generate explanation for formula {formula.id}: {e}")

        # 3. Generate Reviewer Critique
        critique_prompt = REVIEWER_CRITIQUE_PROMPT.format(paper_content=paper_content)
        reviewer_critique = self.llm_client.generate_structured(
            prompt=critique_prompt,
            response_model=ReviewerCritique
        )

        # 4. Construct and Return Final Report
        report = AnalysisReport(
            executive_summary=summary_result.executive_summary,
            core_problem=summary_result.core_problem,
            key_innovation=summary_result.key_innovation,
            methodology_overview=summary_result.methodology_overview,
            formula_explanations=formula_explanations,
            reviewer_critique=reviewer_critique,
            timestamp=datetime.now(timezone.utc)
        )

        return report
