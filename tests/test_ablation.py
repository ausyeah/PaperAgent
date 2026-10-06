import unittest
import ast
from unittest.mock import patch

from paperagent.models import PaperProject, ParsedPaper, PaperMetadata, PaperSection, ExtractedAlgorithm, SynthesisResult
from paperagent.synthesizer.ablation import AblationGenerator
from paperagent.engine.llm_client import LLMClient

class TestAblationGenerator(unittest.TestCase):
    def setUp(self):
        self.algo = ExtractedAlgorithm(
            id="algo-1",
            name="Transformer",
            pseudocode="def forward(x): return x",
            inputs=["x"],
            outputs=["y"]
        )
        self.paper = ParsedPaper(
            metadata=PaperMetadata(title="Attention Is All You Need", authors=["Vaswani et al."]),
            sections=[
                PaperSection(
                    title="Method",
                    algorithms=[self.algo]
                )
            ]
        )
        self.synthesis = SynthesisResult(
            algorithm_name="Transformer",
            target_module_code="class Transformer:\n    def forward(self, x):\n        return x",
            test_suite_code="def test_transformer(): pass"
        )
        self.project = PaperProject(
            id="proj-1",
            paper=self.paper,
            synthesis=self.synthesis
        )

        # Ensure no real API calls
        self.llm_client = LLMClient()
        self.llm_client.gemini_api_key = None
        self.llm_client.openai_api_key = None

    def test_offline_fallback(self):
        generator = AblationGenerator(llm_client=self.llm_client)
        result = generator.design_ablation_study(project=self.project)
        
        self.assertEqual(result.baseline_algorithm, "Transformer")
        self.assertEqual(result.paper_title, "Attention Is All You Need")
        self.assertGreaterEqual(len(result.variants), 3)
        self.assertLessEqual(len(result.variants), 5)
        
        # Verify it has harness code and it's valid syntax
        self.assertTrue(len(result.ablation_harness_code) > 0)
        try:
            ast.parse(result.ablation_harness_code)
        except SyntaxError as e:
            self.fail(f"Harness code has invalid syntax: {e}")
            
        # Verify offline variants
        variant_names = [v.variant_name for v in result.variants]
        self.assertIn("No Normalization", variant_names)

    @patch("paperagent.engine.llm_client.LLMClient.generate_structured")
    def test_mocked_llm(self, mock_generate):
        from paperagent.models import AblationStudyResult, AblationVariant
        mock_generate.return_value = AblationStudyResult(
            paper_title="Mocked Title",
            baseline_algorithm="Transformer",
            variants=[
                AblationVariant(
                    variant_name="Mock Variant",
                    modified_component="Mock Component",
                    hypothesis="Mock Hypothesis"
                )
            ],
            ablation_harness_code="def harness(): pass",
            insights_summary="Mock Insights"
        )
        
        # Simulate having an API key to bypass offline check
        self.llm_client.openai_api_key = "fake_key"
        
        generator = AblationGenerator(llm_client=self.llm_client)
        result = generator.design_ablation_study(project=self.project)
        
        self.assertEqual(result.baseline_algorithm, "Transformer")
        # Ensure it didn't overwrite the mocked value entirely if it existed, 
        # or that it set missing fields based on the project if we mocked it that way
        # Since we gave it a title in the mock, it should keep it (but the method fills if empty).
        self.assertEqual(result.paper_title, "Mocked Title")
        self.assertEqual(len(result.variants), 1)
        self.assertEqual(result.variants[0].variant_name, "Mock Variant")

if __name__ == '__main__':
    unittest.main()