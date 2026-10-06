import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from paperagent.models import ExtractedFormula, TensorDimensionCheck, FormulaVerificationReport
from paperagent.engine.formula_checker import FormulaDimensionChecker


def test_verify_formula_offline_mode_attention():
    """Test the mock offline verification specifically matching the attention formula."""
    checker = FormulaDimensionChecker()
    formula = ExtractedFormula(
        id="eq-1",
        latex=r"Q K^T / \sqrt{d_k}",
        context_text="Attention mechanism"
    )

    report = checker._mock_verification(formula)

    assert report.formula_id == "eq-1"
    assert report.latex == r"Q K^T / \sqrt{d_k}"
    assert report.invariants_passed is True
    assert len(report.dimensions) == 3
    assert report.dimensions[0].variable_name == "Q"
    assert report.dimensions[0].expected_shape == "(B, H, S, D/H)"


def test_verify_formula_offline_mode_generic():
    """Test the generic mock offline verification."""
    checker = FormulaDimensionChecker()
    formula = ExtractedFormula(
        id="eq-2",
        latex=r"y = Wx + b",
        context_text="Linear layer"
    )

    report = checker._mock_verification(formula)

    assert report.formula_id == "eq-2"
    assert report.invariants_passed is True
    assert len(report.dimensions) == 1
    assert report.dimensions[0].variable_name == "X"
    assert report.dimensions[0].expected_shape == "(B, C, H, W)"


@patch("paperagent.engine.llm_client.LLMClient.generate_structured_async", new_callable=AsyncMock)
def test_verify_formula_llm_mode(mock_generate):
    """Test the LLM mode correctly parses the returned structured response."""
    # Create the mock returned report
    mock_report = FormulaVerificationReport(
        formula_id="dummy",  # the checker will override this
        latex="dummy",       # the checker will override this
        dimensions=[
            TensorDimensionCheck(
                variable_name="x",
                expected_shape="(N, D)",
                math_symbol="x",
                is_consistent=True,
                explanation="Input data"
            )
        ],
        invariants_passed=True,
        dimension_notes="All good."
    )
    mock_generate.return_value = mock_report

    checker = FormulaDimensionChecker()
    formula = ExtractedFormula(
        id="eq-3",
        latex=r"x \in \mathbb{R}^{N \times D}",
        context_text="Input data representation"
    )

    report = checker.verify_formula(formula)

    # Check if prompt was sent properly
    mock_generate.assert_called_once()
    kwargs = mock_generate.call_args.kwargs
    assert "prompt" in kwargs
    assert formula.latex in kwargs["prompt"]

    # Check report fields
    assert report.formula_id == "eq-3"
    assert report.latex == r"x \in \mathbb{R}^{N \times D}"
    assert report.invariants_passed is True
    assert len(report.dimensions) == 1
    assert report.dimensions[0].variable_name == "x"
    assert report.dimensions[0].expected_shape == "(N, D)"
    assert report.dimension_notes == "All good."
