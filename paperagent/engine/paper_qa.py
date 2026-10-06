import logging
from typing import Optional, List, Dict
import re

from paperagent.engine.llm_client import LLMClient
from paperagent.models import PaperProject, QAResponse, GroundedCitation
from paperagent.engine.prompts import PAPER_QA_PROMPT

logger = logging.getLogger(__name__)

class PaperQAAgent:
    """Conversational QA assistant for academic papers with grounded citations."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def answer_question(self, query: str, project: PaperProject) -> QAResponse:
        """
        Answers a user query based on the paper content, providing grounded citations.
        Includes an offline fallback using keyword overlap if LLM is unavailable.
        """
        # Collect context from sections and formulas
        context_parts = []
        for section in project.paper.sections:
            context_parts.append(f"Section: {section.title}\n{section.content}")
            for formula in section.formulas:
                context_parts.append(f"Formula ID: {formula.id}\nLaTeX: {formula.latex}\nContext: {formula.context_text}")
        
        context_text = "\n\n".join(context_parts)

        # Check if we should use offline fallback
        if not self.llm_client.gemini_api_key and not self.llm_client.openai_api_key:
            return self._offline_fallback(query, project)

        prompt = PAPER_QA_PROMPT.format(query=query, context=context_text)

        try:
            response = self.llm_client.generate_structured(
                prompt=prompt,
                response_model=QAResponse,
                system_prompt="You are an expert AI research assistant. Provide concise, authoritative answers based only on the provided context."
            )
            response.query = query
            return response
        except Exception as e:
            logger.warning(f"LLM generation failed for QA: {e}. Falling back to offline method.")
            return self._offline_fallback(query, project)

    def _offline_fallback(self, query: str, project: PaperProject) -> QAResponse:
        """Heuristic fallback using keyword overlap to find relevant sections/formulas."""
        query_words = set(re.findall(r'\w+', query.lower()))
        
        best_section = None
        best_score = 0
        best_sentence = ""

        for section in project.paper.sections:
            words = set(re.findall(r'\w+', section.content.lower()))
            overlap = len(query_words.intersection(words))
            
            if overlap > best_score:
                best_score = overlap
                best_section = section
                
                # Find a relevant sentence
                sentences = re.split(r'(?<=[.!?])\s+', section.content)
                for sentence in sentences:
                    s_words = set(re.findall(r'\w+', sentence.lower()))
                    if query_words.intersection(s_words):
                        best_sentence = sentence
                        break

        citations = []
        if best_section:
            citations.append(GroundedCitation(
                section_title=best_section.title,
                relevant_quote=best_sentence.strip()
            ))
            answer = f"Based on keyword matching in section '{best_section.title}': {best_sentence.strip()}"
            confidence_score = min(best_score / (len(query_words) or 1) * 0.5, 0.5)
        else:
            answer = "I could not find a relevant answer in the paper text."
            confidence_score = 0.0

        return QAResponse(
            query=query,
            answer=answer,
            citations=citations,
            confidence_score=confidence_score
        )


def answer_paper_question(query: str, project: PaperProject, client: Optional[LLMClient] = None) -> QAResponse:
    """Convenience helper to answer a question about a paper."""
    agent = PaperQAAgent(llm_client=client)
    return agent.answer_question(query, project)