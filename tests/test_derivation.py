import pytest
from paperagent.models import ExtractedFormula, DerivationVerificationResult, DerivationStep
from paperagent.engine.derivation import DerivationVerifier
from paperagent.engine.llm_client import LLMClient
from unittest.mock import MagicMock

def test_offline_fallback_sequence():
    """Test that DerivationVerifier falls back to offline steps correctly."""
    # Create mock formulas
    formula_from = ExtractedFormula(
        id="eq-1",
        latex="a^2 + b^2 = c^2",
        context_text="Pythagorean theorem base."
    )
    formula_to = ExtractedFormula(
        id="eq-2",
        latex="c = \\sqrt{a^2 + b^2}",
        context_text="Solved for c."
    )
    
    # Create verifier with mock LLM client containing no API keys
    mock_llm = MagicMock(spec=LLMClient)
    mock_llm.gemini_api_key = None
    mock_llm.openai_api_key = None
    
    verifier = DerivationVerifier(llm_client=mock_llm)
    
    # Run verification
    result = verifier.verify_derivation_steps(formula_from, formula_to)
    
    # Assert result structure and offline fallback values
    assert isinstance(result, DerivationVerificationResult)
    assert result.formula_from_id == "eq-1"
    assert result.formula_to_id == "eq-2"
    assert len(result.steps) == 3
    
    # Check step sequence
    assert result.steps[0].step_number == 1
    assert "expansion" in result.steps[0].latex_expression
    
    assert result.steps[1].step_number == 2
    assert "intermediate substitution" in result.steps[1].latex_expression
    
    assert result.steps[2].step_number == 3
    assert result.steps[2].latex_expression == formula_to.latex
    
    # Check soundness and notes
    assert result.is_mathematically_sound is True
    assert "[Offline Fallback]" in result.algebraic_notes

def test_llm_mode():
    """Test that DerivationVerifier uses LLM when API keys are available."""
    formula_from = ExtractedFormula(
        id="eq-1",
        latex="x + x",
        context_text="Start"
    )
    formula_to = ExtractedFormula(
        id="eq-2",
        latex="2x",
        context_text="End"
    )
    
    # Mock LLMClient that returns a structured result
    mock_llm = MagicMock(spec=LLMClient)
    mock_llm.gemini_api_key = "fake_key"
    mock_llm.openai_api_key = None
    
    expected_result = DerivationVerificationResult(
        formula_from_id="eq-1",
        formula_to_id="eq-2",
        steps=[DerivationStep(step_number=1, latex_expression="x+x=2x", justification="Addition")],
        is_mathematically_sound=True,
        algebraic_notes="Looks good."
    )
    mock_llm.generate_structured.return_value = expected_result
    
    verifier = DerivationVerifier(llm_client=mock_llm)
    result = verifier.verify_derivation_steps(formula_from, formula_to)
    
    # The verifier should return the LLM's result directly (but with matched IDs)
    assert result == expected_result
    mock_llm.generate_structured.assert_called_once()