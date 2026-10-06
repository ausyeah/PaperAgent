"""
Tests for Core Models & Config
Works both with standard unittest and pytest.
"""

import unittest
from paperagent.models import (
    PaperMetadata,
    ExtractedFormula,
    ExtractedAlgorithm,
    PaperSection,
    ParsedPaper,
    FormulaExplanation,
    ReviewerCritique,
    AnalysisReport,
    ExecutionResult,
    SynthesisResult,
    PaperProject,
)
from paperagent.config import settings


class TestModels(unittest.TestCase):
    def test_paper_metadata_creation(self):
        meta = PaperMetadata(
            title="Attention Is All You Need",
            authors=["Vaswani et al."],
            abstract="The dominant sequence transduction models...",
            arxiv_id="1706.03762",
            year=2017,
            categories=["cs.CL"]
        )
        self.assertEqual(meta.title, "Attention Is All You Need")
        self.assertEqual(meta.arxiv_id, "1706.03762")
        self.assertEqual(len(meta.authors), 1)

    def test_parsed_paper_structure(self):
        meta = PaperMetadata(title="Test Paper", authors=["Author"])
        formula = ExtractedFormula(id="eq-1", latex=r"\text{Softmax}(z)", context_text="Softmax function")
        algo = ExtractedAlgorithm(id="algo-1", name="Algorithm 1", pseudocode="for i in range(n): pass")
        section = PaperSection(
            title="Introduction",
            level=1,
            content="Intro text",
            formulas=[formula],
            algorithms=[algo]
        )
        paper = ParsedPaper(
            metadata=meta,
            sections=[section],
            raw_markdown="# Introduction\nIntro text",
            source_type="arxiv"
        )
        self.assertEqual(len(paper.sections), 1)
        self.assertEqual(paper.sections[0].formulas[0].id == "eq-1", True)
        self.assertEqual(paper.sections[0].algorithms[0].id == "algo-1", True)

    def test_analysis_report_validation(self):
        critique = ReviewerCritique(
            strengths=["Novel transformer architecture"],
            weaknesses=["High computational complexity for very long sequences"],
            score=9
        )
        report = AnalysisReport(
            executive_summary="Groundbreaking attention mechanism",
            core_problem="Recurrence bottleneck in sequential computation",
            key_innovation="Self-attention mechanism",
            methodology_overview="Multi-head attention with sinusoidal positional encoding",
            reviewer_critique=critique
        )
        self.assertEqual(report.reviewer_critique.score, 9)
        self.assertTrue(report.reviewer_critique.strengths[0].startswith("Novel"))

    def test_synthesis_result(self):
        res = SynthesisResult(
            algorithm_name="SelfAttention",
            target_module_code="import torch\ndef attention(): pass",
            test_suite_code="def test_attention(): assert True",
            execution_result=ExecutionResult(
                success=True,
                exit_code=0,
                stdout="Ran 1 test. OK",
                execution_time_seconds=0.15
            )
        )
        self.assertTrue(res.execution_result.success)
        self.assertEqual(res.execution_result.exit_code, 0)

    def test_settings_initialization(self):
        self.assertTrue(settings.base_dir.exists())
        self.assertTrue(settings.data_dir.exists())


if __name__ == "__main__":
    unittest.main()
