import re
from typing import Set

from paperagent.models import CanonicalMathExpression, MathNormalizationCollection, ParsedPaper


class MathNormalizer:
    """
    Canonicalizes raw LaTeX equations and normalizes them for SymPy.
    """

    def normalize_latex(self, latex_str: str) -> CanonicalMathExpression:
        r"""
        Cleans and canonicalizes raw LaTeX equations.
        Strips \left, \right, whitespace quirks, normalizes fractions \frac{a}{b} -> a/b,
        converts superscripts/subscripts.
        Extracts unique math symbol tokens.
        Generates normalized SymPy-compatible expression string.
        """
        original_latex = latex_str
        
        # 1. Clean whitespace
        latex_str = re.sub(r'\s+', ' ', latex_str).strip()
        
        # 2. Strip \left and \right
        latex_str = latex_str.replace(r'\left(', '(').replace(r'\right)', ')')
        latex_str = latex_str.replace(r'\left[', '[').replace(r'\right]', ']')
        latex_str = latex_str.replace(r'\left\{', '{').replace(r'\right\}', '}')
        latex_str = latex_str.replace(r'\left', '').replace(r'\right', '')
        
        # 3. Normalize fractions
        latex_str = self._normalize_fractions(latex_str)
        
        # 4. Normalize superscripts: a^{b} -> a**(b), a^b -> a**b
        latex_str = re.sub(r'\^\{([^}]+)\}', r'**(\1)', latex_str)
        latex_str = re.sub(r'\^([a-zA-Z0-9])', r'**\1', latex_str)
        
        # 5. Normalize subscripts: a_{b} -> a_b
        latex_str = re.sub(r'_\{([^}]+)\}', r'_\1', latex_str)
        
        # 6. Basic operations
        latex_str = latex_str.replace(r'\cdot', '*')
        latex_str = latex_str.replace(r'\times', '*')
        
        # Final whitespace clean (in case stripping left/right left spaces)
        latex_str = latex_str.replace(' ', '')
        
        # Extract symbols
        symbols = self._extract_symbols(original_latex)
        
        return CanonicalMathExpression(
            original_latex=original_latex,
            canonical_sympy=latex_str,
            symbols=sorted(list(symbols)),
            is_solvable=True
        )
        
    def _normalize_fractions(self, text: str) -> str:
        r"""Converts \frac{a}{b} into (a)/(b) handling nested brackets."""
        while r'\frac' in text:
            idx = text.find(r'\frac')
            
            # Find numerator
            start1 = text.find('{', idx)
            if start1 == -1:
                break
            end1 = start1
            depth = 0
            for i in range(start1, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        end1 = i
                        break
            
            # Find denominator
            start2 = text.find('{', end1 + 1)
            if start2 == -1:
                break
            end2 = start2
            depth = 0
            for i in range(start2, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        end2 = i
                        break
            
            # Just in case of malformed LaTeX
            if end1 == start1 or end2 == start2:
                break
                
            num = text[start1+1:end1]
            den = text[start2+1:end2]
            
            # Replace
            text = text[:idx] + f"({num})/({den})" + text[end2+1:]
        return text
        
    def _extract_symbols(self, latex_str: str) -> Set[str]:
        """Extracts math symbols like English letters and Greek variables."""
        symbols = set()
        
        # Greek letters
        greeks = [
            r'\alpha', r'\beta', r'\gamma', r'\delta', r'\epsilon', r'\zeta', 
            r'\eta', r'\theta', r'\iota', r'\kappa', r'\lambda', r'\mu', 
            r'\nu', r'\xi', r'\omicron', r'\pi', r'\rho', r'\sigma', r'\tau', 
            r'\upsilon', r'\phi', r'\chi', r'\psi', r'\omega',
            r'\Gamma', r'\Delta', r'\Theta', r'\Lambda', r'\Xi', r'\Pi', 
            r'\Sigma', r'\Upsilon', r'\Phi', r'\Psi', r'\Omega'
        ]
        
        for g in greeks:
            if g in latex_str:
                symbols.add(g.replace('\\', ''))
                
        # Remove commands to isolate standard English letters
        no_cmds = re.sub(r'\\[a-zA-Z]+', '', latex_str)
        # Find all single alphabetic characters
        letters = re.findall(r'[a-zA-Z]', no_cmds)
        
        symbols.update(letters)
        return symbols

    def normalize_paper_formulas(self, paper: ParsedPaper) -> MathNormalizationCollection:
        """Processes all extracted formulas in a paper."""
        expressions = []
        if paper.sections:
            for section in paper.sections:
                if section.formulas:
                    for formula in section.formulas:
                        try:
                            normalized = self.normalize_latex(formula.latex)
                            expressions.append(normalized)
                        except Exception as e:
                            # Robust error handling: skip formula on failure or return original
                            expressions.append(CanonicalMathExpression(
                                original_latex=formula.latex,
                                canonical_sympy=formula.latex,
                                symbols=[],
                                is_solvable=False
                            ))
                        
        return MathNormalizationCollection(
            paper_title=paper.metadata.title,
            expressions=expressions
        )