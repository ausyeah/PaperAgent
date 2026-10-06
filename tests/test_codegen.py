import ast
import unittest
from paperagent.models import ExtractedAlgorithm, PaperMetadata, PaperSection, ParsedPaper
from paperagent.synthesizer.code_generator import CodeGenerator
from paperagent.synthesizer.test_generator import TestGenerator
from paperagent.synthesizer import CodeSynthesizer

class TestCodeSynthesis(unittest.TestCase):

    def setUp(self):
        self.algo = ExtractedAlgorithm(
            id="algo-1",
            name="Momentum Contrast",
            pseudocode="initialize...",
            inputs=["X"],
            outputs=["y"]
        )
        self.paper = ParsedPaper(
            metadata=PaperMetadata(title="MoCo", authors=["He"]),
            sections=[
                PaperSection(
                    title="Method",
                    algorithms=[self.algo]
                )
            ]
        )

    def test_code_generator_valid_syntax(self):
        codegen = CodeGenerator()
        code = codegen.generate_code(algo=self.algo)

        self.assertIsInstance(code, str)
        self.assertTrue(len(code) > 0)

        # Verify it is valid Python syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Generated code has invalid syntax: {e}")

        self.assertIn("class MomentumContrast", code)
        self.assertIn("def fit", code)
        self.assertIn("def predict", code)
        self.assertIn("if __name__ == '__main__':", code)

    def test_test_generator_valid_syntax(self):
        testgen = TestGenerator()
        code = testgen.generate_test_suite(generated_code="class MomentumContrast: pass", algo=self.algo)

        self.assertIsInstance(code, str)
        self.assertTrue(len(code) > 0)

        # Verify it is valid Python syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.fail(f"Generated test code has invalid syntax: {e}")

        self.assertIn("def test_shape_checks", code)
        self.assertIn("def test_numerical_stability", code)

    def test_code_synthesizer(self):
        synthesizer = CodeSynthesizer()
        result = synthesizer.synthesize(paper=self.paper, algo_index=0)

        self.assertEqual(result.algorithm_name, "Momentum Contrast")
        self.assertTrue(len(result.target_module_code) > 0)
        self.assertTrue(len(result.test_suite_code) > 0)

        # Verify both outputs are syntactically valid
        try:
            ast.parse(result.target_module_code)
            ast.parse(result.test_suite_code)
        except SyntaxError as e:
            self.fail(f"Synthesized code has invalid syntax: {e}")

if __name__ == '__main__':
    unittest.main()
