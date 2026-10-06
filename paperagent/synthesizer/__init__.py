from typing import Optional
from paperagent.models import ParsedPaper, SynthesisResult
from paperagent.synthesizer.code_generator import CodeGenerator
from paperagent.synthesizer.test_generator import TestGenerator

class CodeSynthesizer:
    """
    Synthesizes code and tests from a ParsedPaper.
    """

    def __init__(self) -> None:
        self.code_gen = CodeGenerator()
        self.test_gen = TestGenerator()

    def synthesize(self, paper: ParsedPaper, algo_index: int = 0) -> SynthesisResult:
        """
        Synthesize runnable Python code and tests for the paper's algorithm.
        """
        all_algorithms = []
        for section in paper.sections:
            if section.algorithms:
                all_algorithms.extend(section.algorithms)

        algo = None
        if all_algorithms and len(all_algorithms) > algo_index:
            algo = all_algorithms[algo_index]

        algo_name = algo.name if algo else "PaperAlgorithm"

        target_module_code = self.code_gen.generate_code(algo=algo, sections=paper.sections)
        test_suite_code = self.test_gen.generate_test_suite(generated_code=target_module_code, algo=algo)

        return SynthesisResult(
            algorithm_name=algo_name,
            target_module_code=target_module_code,
            test_suite_code=test_suite_code,
            toy_benchmark_code=None,
            execution_result=None,
            jupyter_notebook_json=None
        )
