import logging
import asyncio
from typing import Optional

from paperagent.models import ParsedPaper, HybridSynthesisResult
from paperagent.engine.llm_client import LLMClient
from paperagent.engine.prompts import CROSS_PAPER_FUSION_PROMPT

logger = logging.getLogger(__name__)

class CrossPaperFusionSynthesizer:
    """
    Synthesizes a unified hybrid algorithm from two distinct academic papers,
    identifying complementary strengths and generating robust code.
    """

    def fuse_papers(
        self, 
        paper_a: ParsedPaper, 
        paper_b: ParsedPaper, 
        client: Optional[LLMClient] = None
    ) -> HybridSynthesisResult:
        """Synchronous wrapper for cross-paper fusion."""
        return asyncio.run(self.fuse_papers_async(paper_a, paper_b, client))

    async def fuse_papers_async(
        self,
        paper_a: ParsedPaper,
        paper_b: ParsedPaper,
        client: Optional[LLMClient] = None
    ) -> HybridSynthesisResult:
        """
        Asynchronously synthesizes a unified hybrid algorithm from two distinct academic papers.
        """
        client = client or LLMClient()
        
        prompt = CROSS_PAPER_FUSION_PROMPT.format(
            paper_a_content=paper_a.model_dump_json(indent=2),
            paper_b_content=paper_b.model_dump_json(indent=2)
        )
        
        try:
            logger.info(f"Synthesizing hybrid algorithm from '{paper_a.metadata.title}' and '{paper_b.metadata.title}'")
            result = await client.generate_structured_async(
                prompt=prompt,
                response_model=HybridSynthesisResult,
                system_prompt="You are a brilliant AI algorithms engineer and research scientist."
            )
            return result
        except Exception as e:
            logger.error(f"Failed to synthesize hybrid algorithm: {e}")
            return self._get_fallback_result(paper_a, paper_b)

    def _get_fallback_result(self, paper_a: ParsedPaper, paper_b: ParsedPaper) -> HybridSynthesisResult:
        """Robust offline fallback for HybridSynthesisResult when LLM is unavailable."""
        import re
        name_a = re.sub(r'[^a-zA-Z0-9]', '', paper_a.metadata.title.split()[0])
        name_b = re.sub(r'[^a-zA-Z0-9]', '', paper_b.metadata.title.split()[0])
        hybrid_name = f"Hybrid_{name_a}_{name_b}"
        
        hybrid_code = f'''import torch
import torch.nn as nn

class {hybrid_name}(nn.Module):
    """
    Fallback mock hybrid algorithm combining features from:
    - {paper_a.metadata.title}
    - {paper_b.metadata.title}
    """
    def __init__(self, dim=256):
        super().__init__()
        self.dim = dim
        self.proj = nn.Linear(dim, dim)
        self.activation = nn.GELU()

    def forward(self, x):
        return self.activation(self.proj(x))
'''

        test_code = f'''import pytest
import torch
from hybrid_module import {hybrid_name}

def test_{hybrid_name.lower()}_forward():
    model = {hybrid_name}(dim=128)
    x = torch.randn(2, 16, 128)
    out = model(x)
    assert out.shape == (2, 16, 128)
    assert not torch.isnan(out).any()
'''

        return HybridSynthesisResult(
            source_paper_a=paper_a.metadata.title,
            source_paper_b=paper_b.metadata.title,
            hybrid_algorithm_name=hybrid_name,
            fusion_rationale=f"Offline fallback fusion of {paper_a.metadata.title} and {paper_b.metadata.title}. The complementary strengths are assumed to be robust feature extraction combined with efficient state representations.",
            hybrid_code=hybrid_code,
            test_suite_code=test_code
        )