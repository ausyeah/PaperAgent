import re
from typing import Optional
from paperagent.models import ExtractedAlgorithm
from paperagent.engine.llm_client import LLMClient

class TestGenerator:
    """
    Generates accompanying automated test suite with assertions verifying mathematical invariants, shape checks, and numerical stability.
    """
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def generate_test_suite(self, generated_code: str, algo: Optional[ExtractedAlgorithm] = None) -> str:
        """
        Generates Python test suite code based on an ExtractedAlgorithm and the generated module code.
        Returns a syntactically valid Python string using pytest.
        """
        algo_name = algo.name if algo else "the algorithm"
        prompt = f"""
        Given the following Python implementation of {algo_name}:

        ```python
        {generated_code}
        ```

        Generate an accompanying automated test suite using pytest.
        Include assertions verifying mathematical invariants, shape checks, and numerical stability based on the provided implementation.

        Please return ONLY valid Python test suite code, without any introductory or concluding text. Do not wrap with ```python ... ```.
        """

        generated_test_code = self.llm_client.generate(prompt)

        # Cleanup potential markdown formatting
        generated_test_code = re.sub(r"^```python\s*", "", generated_test_code, flags=re.IGNORECASE)
        generated_test_code = re.sub(r"\s*```$", "", generated_test_code)

        return generated_test_code.strip()
