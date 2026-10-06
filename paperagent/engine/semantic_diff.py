from typing import Optional, Dict

from paperagent.models import ParsedPaper, PaperSemanticDiff, SemanticDiffItem
from paperagent.engine.prompts import SEMANTIC_DIFF_PROMPT
from paperagent.engine.llm_client import LLMClient

class PaperSemanticDiffEngine:
    """
    Engine for identifying semantic differences and evolution between two versions of a paper.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the PaperSemanticDiffEngine.

        Args:
            llm_client (Optional[LLMClient]): The LLM client to use.
        """
        self.llm_client = llm_client or LLMClient()

    def diff_papers(self, paper_v1: ParsedPaper, paper_v2: ParsedPaper, client: Optional[LLMClient] = None) -> PaperSemanticDiff:
        """
        Compares two versions of a paper (e.g. ArXiv v1 vs v2).
        Identifies added, removed, and modified sections, changes in experimental metrics, and revised claims.

        Args:
            paper_v1 (ParsedPaper): The first version of the paper.
            paper_v2 (ParsedPaper): The second version of the paper.
            client (Optional[LLMClient]): Optionally override the engine's LLM client.

        Returns:
            PaperSemanticDiff: The semantic diff between the two versions.
        """
        llm = client or self.llm_client

        title = paper_v1.metadata.title if paper_v1.metadata.title else paper_v2.metadata.title

        if not llm.gemini_api_key and not llm.openai_api_key:
            return self._offline_diff(paper_v1, paper_v2)

        v1_content = self._format_paper_content(paper_v1)
        v2_content = self._format_paper_content(paper_v2)

        prompt = SEMANTIC_DIFF_PROMPT.format(
            paper_v1_content=v1_content,
            paper_v2_content=v2_content
        )

        try:
            diff = llm.generate_structured(prompt=prompt, response_model=PaperSemanticDiff)
            # Ensure title is set correctly if LLM missed it
            if not diff.paper_title or diff.paper_title == "Unknown Title":
                diff.paper_title = title
            return diff
        except Exception:
            return self._offline_diff(paper_v1, paper_v2)

    def _format_paper_content(self, paper: ParsedPaper) -> str:
        """Helper to format paper content for the LLM."""
        content = f"Title: {paper.metadata.title}\n"
        content += f"Abstract: {paper.metadata.abstract}\n\n"
        for section in paper.sections:
            content += f"## {section.title}\n"
            content += f"{section.content}\n\n"
        return content

    def _offline_diff(self, paper_v1: ParsedPaper, paper_v2: ParsedPaper) -> PaperSemanticDiff:
        """
        Deterministic offline text-matching fallback.
        """
        title = paper_v1.metadata.title if paper_v1.metadata.title else paper_v2.metadata.title
        diff_items = []

        v1_sections: Dict[str, str] = {s.title: s.content for s in paper_v1.sections}
        v2_sections: Dict[str, str] = {s.title: s.content for s in paper_v2.sections}

        all_titles = set(v1_sections.keys()).union(set(v2_sections.keys()))

        for sec_title in all_titles:
            v1_content = v1_sections.get(sec_title)
            v2_content = v2_sections.get(sec_title)

            if v1_content is None and v2_content is not None:
                diff_items.append(SemanticDiffItem(
                    section_title=sec_title,
                    change_type="added",
                    v1_summary="",
                    v2_summary=v2_content[:100] + "..." if len(v2_content) > 100 else v2_content,
                    significance="Medium"
                ))
            elif v1_content is not None and v2_content is None:
                diff_items.append(SemanticDiffItem(
                    section_title=sec_title,
                    change_type="removed",
                    v1_summary=v1_content[:100] + "..." if len(v1_content) > 100 else v1_content,
                    v2_summary="",
                    significance="Medium"
                ))
            elif v1_content is not None and v2_content is not None:
                if v1_content.strip() != v2_content.strip():
                    diff_items.append(SemanticDiffItem(
                        section_title=sec_title,
                        change_type="modified",
                        v1_summary=v1_content[:100] + "..." if len(v1_content) > 100 else v1_content,
                        v2_summary=v2_content[:100] + "..." if len(v2_content) > 100 else v2_content,
                        significance="Low"
                    ))

        return PaperSemanticDiff(
            paper_title=title,
            v1_identifier="v1",
            v2_identifier="v2",
            diff_items=diff_items,
            executive_diff_summary="Offline fallback diff generated."
        )

def diff_papers(paper_v1: ParsedPaper, paper_v2: ParsedPaper, client: Optional[LLMClient] = None) -> PaperSemanticDiff:
    """Convenience helper to diff two papers."""
    engine = PaperSemanticDiffEngine(llm_client=client)
    return engine.diff_papers(paper_v1, paper_v2, client)
