import pytest
from paperagent.models import ParsedPaper, PaperMetadata, PaperSection, ExtractedFormula
from paperagent.parser.math_normalizer import MathNormalizer

def test_normalize_fractions():
    normalizer = MathNormalizer()
    latex = r"\frac{a}{b}"
    result = normalizer.normalize_latex(latex)
    assert result.canonical_sympy == "(a)/(b)"

def test_normalize_nested_fractions():
    normalizer = MathNormalizer()
    latex = r"\frac{\frac{a}{b}}{c}"
    result = normalizer.normalize_latex(latex)
    assert result.canonical_sympy == "((a)/(b))/(c)"

def test_normalize_powers():
    normalizer = MathNormalizer()
    latex = r"x^{2}"
    result = normalizer.normalize_latex(latex)
    assert result.canonical_sympy == "x**(2)"
    
    latex2 = r"e^x"
    result2 = normalizer.normalize_latex(latex2)
    assert result2.canonical_sympy == "e**x"

def test_normalize_subscripts():
    normalizer = MathNormalizer()
    latex = r"x_{i}"
    result = normalizer.normalize_latex(latex)
    assert result.canonical_sympy == "x_i"

def test_extract_symbols_greek():
    normalizer = MathNormalizer()
    latex = r"\alpha + \beta = \gamma"
    result = normalizer.normalize_latex(latex)
    assert "alpha" in result.symbols
    assert "beta" in result.symbols
    assert "gamma" in result.symbols

def test_strip_left_right():
    normalizer = MathNormalizer()
    latex = r"\left( \frac{a}{b} \right)"
    result = normalizer.normalize_latex(latex)
    assert result.canonical_sympy == "((a)/(b))"

def test_normalize_paper_formulas():
    normalizer = MathNormalizer()
    
    # Mock ParsedPaper
    metadata = PaperMetadata(title="Test Paper", authors=[])
    formula1 = ExtractedFormula(id="1", latex=r"\frac{x}{y}")
    formula2 = ExtractedFormula(id="2", latex=r"\alpha^{2}")
    section = PaperSection(title="Method", level=1, formulas=[formula1, formula2])
    paper = ParsedPaper(metadata=metadata, sections=[section])
    
    result_collection = normalizer.normalize_paper_formulas(paper)
    
    assert result_collection.paper_title == "Test Paper"
    assert len(result_collection.expressions) == 2
    assert result_collection.expressions[0].canonical_sympy == "(x)/(y)"
    assert result_collection.expressions[1].canonical_sympy == r"\alpha**(2)"
    assert "alpha" in result_collection.expressions[1].symbols

def test_normalize_paper_formulas_error_handling():
    normalizer = MathNormalizer()
    
    class MockFormula:
        def __init__(self, latex):
            self.latex = latex
            # Missing id to cause error if accessed improperly, but we only access latex
            # Let's break the normalizer by passing a None which will cause string operations to fail
        
        @property
        def latex(self):
            return None
            
        @latex.setter
        def latex(self, value):
            self._latex = value

    metadata = PaperMetadata(title="Test Paper", authors=[])
    # Pass an ExtractedFormula with weird type or we could just test the exception catching
    # However we can just mock the normalize_latex to raise an exception
    formula = ExtractedFormula(id="1", latex=r"something")
    section = PaperSection(title="Method", level=1, formulas=[formula])
    paper = ParsedPaper(metadata=metadata, sections=[section])
    
    # Monkeypatch the normalize_latex to simulate a crash
    original_normalize_latex = normalizer.normalize_latex
    def fake_normalize(latex):
        raise ValueError("Simulated crash")
    normalizer.normalize_latex = fake_normalize
    
    result_collection = normalizer.normalize_paper_formulas(paper)
    
    assert result_collection.paper_title == "Test Paper"
    assert len(result_collection.expressions) == 1
    assert result_collection.expressions[0].is_solvable == False
    assert result_collection.expressions[0].original_latex == "something"
    
    # Restore
    normalizer.normalize_latex = original_normalize_latex