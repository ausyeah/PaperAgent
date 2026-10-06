"""
Prompt templates for the PaperAgent AI Reasoning Engine.
"""

EXECUTIVE_SUMMARY_PROMPT = """
You are an expert AI research assistant. Your task is to provide a comprehensive executive summary of the following academic paper.

Based on the parsed paper content provided, you need to extract and synthesize the following:
1. Executive Summary: A high-level 3-minute executive summary.
2. Core Problem: What fundamental problem does this paper solve?
3. Key Innovation: The key trick or breakthrough insight introduced by the authors.
4. Methodology Overview: A systematic walk-through of the proposed method.

Paper Content:
{paper_content}

Return the output formatted strictly according to the requested structure.
"""

FORMULA_EXPLAINER_PROMPT = """
You are an expert mathematical demystifier and AI researcher. Your task is to explain the following mathematical formula from an academic paper in an intuitive, easy-to-understand way.

Formula (LaTeX): {latex}
Context from paper: {context}

Please provide:
1. Variable Glossary: A mapping of variables to their real-world meanings.
2. Intuitive Intuition: Why this formula was designed this way, in plain English.
3. Step-by-Step Breakdown: A systematic explanation of each part of the formula.

Return the output strictly according to the requested structure.
"""

REVIEWER_CRITIQUE_PROMPT = """
You are a highly critical and insightful reviewer for a top-tier machine learning conference (e.g., NeurIPS, ICLR, ICML).
Your task is to provide a rigorous critique of the following academic paper.

Please evaluate the paper based on the following criteria and provide:
1. Strengths: Core novelties, solid empirical findings, and important contributions.
2. Weaknesses: Hidden assumptions, unproven claims, missing baselines, or limitations.
3. Boundary Conditions: When does this algorithm fail or degrade? What are its fundamental limitations?
4. Potential Reproducibility Pitfalls: Ambiguous implementation details, missing hyperparameter specs, or unclear evaluation metrics.
5. Score: An overall recommendation score from 1 to 10 (1=Strong Reject, 10=Strong Accept).

Paper Content:
{paper_content}

Return the output strictly according to the requested structure.
"""

COMPARATOR_PROMPT = """
You are an expert AI researcher tasked with deeply comparing two academic papers.
Your goal is to provide a structured, head-to-head evaluation.

Paper A Content:
{paper_a_content}

Paper B Content:
{paper_b_content}

Please evaluate and compare the two papers across the following key dimensions:
1. Inductive Bias & Core Approach
2. Mathematical Formulation
3. Computational Complexity (Time & Memory)
4. Empirical Benchmarks & Datasets
5. Practical Deployment & Hardware Requirements

Return a structured ComparisonMatrix that contains:
- paper_a_title and paper_b_title
- A list of `dimensions` detailing the comparison for the above 5 criteria.
- `trade_off_summary`: A brief summary of fundamental engineering trade-offs.
- `recommended_choice`: Actionable guidance on which to use in which scenarios.
"""

CODE_ALIGNER_PROMPT = """
You are an expert software engineer and AI researcher. Your task is to analyze synthesized Python code and align it with the mathematical formulas from the original academic paper.

Paper Title: {paper_title}

Extracted Formulas:
{formulas}

Synthesized Python Code:
{code}

Please bidirectionally map the synthesized code to the mathematical formulas.
Return a structured TraceMap object with a list of `CodeMathAlignment` mappings.
For each alignment, provide:
1. `function_name`: The name of the function or block in the code.
2. `code_line_range`: The line range in the code (e.g., "L12-L28").
3. `target_formula_id`: The ID of the corresponding formula (e.g., "formula-1").
4. `target_formula_latex`: The LaTeX representation of the target formula.
5. `alignment_notes`: An explanation of how the code variables correspond to the math symbols.

Ensure the mapping is as accurate and detailed as possible.
"""
