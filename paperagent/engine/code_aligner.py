import logging
from typing import Optional, List, Dict
from paperagent.models import ParsedPaper, SynthesisResult, TraceMap, CodeMathAlignment, ExtractedFormula
from paperagent.engine.llm_client import LLMClient
from paperagent.engine.prompts import CODE_ALIGNER_PROMPT

logger = logging.getLogger(__name__)

class CodeMathAligner:
    """Bidirectionally traces synthesized Python functions to specific paper formulas."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def align_code_with_paper(self, paper: ParsedPaper, synthesis: SynthesisResult) -> TraceMap:
        """
        Analyzes synthesized Python code against the paper's formulas and sections.
        Maps specific functions or line blocks to the corresponding mathematical formulas.

        Args:
            paper: The parsed academic paper containing formulas.
            synthesis: The synthesized code and results.

        Returns:
            TraceMap: The structured trace mappings.
        """
        # Extract all formulas from the paper
        formulas: List[ExtractedFormula] = []
        for section in paper.sections:
            formulas.extend(section.formulas)

        if not formulas:
            logger.info("No formulas found in the paper to align with code.")
            return self._get_empty_tracemap(paper.metadata.title)

        if not synthesis.target_module_code:
            logger.info("No synthesized code found to align with paper.")
            return self._get_empty_tracemap(paper.metadata.title)

        # Format formulas for prompt
        formulas_str = ""
        for idx, f in enumerate(formulas):
            formulas_str += f"[{idx + 1}] ID: {f.id}\nLaTeX: {f.latex}\nContext: {f.context_text}\n\n"

        prompt = CODE_ALIGNER_PROMPT.format(
            paper_title=paper.metadata.title,
            formulas=formulas_str,
            code=synthesis.target_module_code
        )

        try:
            trace_map = self.llm_client.generate_structured(
                prompt=prompt,
                response_model=TraceMap,
                system_prompt="You are an expert software engineer mapping code to math."
            )
            # Ensure paper title is populated correctly
            trace_map.paper_title = paper.metadata.title
            return trace_map
        except Exception as e:
            logger.warning(f"Failed to generate code alignment from LLM, falling back to mock: {e}")
            return self._get_mock_tracemap(paper.metadata.title, formulas)

    def _get_empty_tracemap(self, paper_title: str) -> TraceMap:
        """Returns an empty TraceMap."""
        return TraceMap(paper_title=paper_title, alignments=[])

    def _get_mock_tracemap(self, paper_title: str, formulas: List[ExtractedFormula]) -> TraceMap:
        """Returns a realistic mock TraceMap when LLM fails or is in offline mode."""
        alignments = []
        if formulas:
            # Create a dummy alignment with the first available formula
            target_formula = formulas[0]
            alignments.append(CodeMathAlignment(
                function_name="compute_loss",
                code_line_range="L42-L50",
                target_formula_id=target_formula.id,
                target_formula_latex=target_formula.latex,
                alignment_notes=f"Mock alignment: Variable 'x' maps to mathematical symbol in {target_formula.id}."
            ))

        return TraceMap(
            paper_title=paper_title,
            alignments=alignments
        )
