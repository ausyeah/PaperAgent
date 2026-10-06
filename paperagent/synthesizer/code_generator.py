import re
from typing import Optional, List
from paperagent.models import ExtractedAlgorithm, PaperSection
from paperagent.engine.llm_client import LLMClient

class CodeGenerator:
    """
    Generates self-contained, high quality Python code implementing a core algorithm.
    """
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def generate_code(self, algo: Optional[ExtractedAlgorithm] = None, sections: Optional[List[PaperSection]] = None) -> str:
        """
        Generates Python code based on an ExtractedAlgorithm or paper methodology sections.
        Returns a syntactically valid Python string.
        """
        algo_name = algo.name if algo else "the algorithm"

        context = ""
        if algo:
            context += f"Algorithm Name: {algo.name}\n"
            if algo.pseudocode:
                context += f"Pseudocode:\n{algo.pseudocode}\n"
            if algo.inputs:
                context += f"Inputs: {', '.join(algo.inputs)}\n"
            if algo.outputs:
                context += f"Outputs: {', '.join(algo.outputs)}\n"
            if algo.complexity:
                context += f"Complexity: {algo.complexity}\n"

        if sections:
            context += "\nRelevant Paper Sections:\n"
            for section in sections:
                context += f"--- {section.title} ---\n{section.content}\n"

        prompt = f"""
        Based on the following extracted information from a paper, generate self-contained, high quality Python code implementing {algo_name}.

        Context:
        {context}

        Requirements:
        - Use only standard library and NumPy/PyTorch.
        - Include full type hints and docstrings.
        - Have an executable demonstration under `if __name__ == '__main__':` with synthetic toy data.

        Please return ONLY valid Python code, without any introductory or concluding text. Do not wrap with ```python ... ```.
        """

        generated_code = self.llm_client.generate(prompt)

        # Cleanup potential markdown formatting
        generated_code = re.sub(r"^```python\s*", "", generated_code, flags=re.IGNORECASE)
        generated_code = re.sub(r"\s*```$", "", generated_code)

        return generated_code.strip()
