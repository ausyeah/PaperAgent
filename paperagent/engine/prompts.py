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

SURVEY_PROMPT = """
You are an expert AI research assistant. Your task is to provide a comprehensive literature survey based on the provided papers about {topic}.

Based on the parsed papers provided, you need to synthesize a structured literature survey with the following:
1. Taxonomy Tree: A hierarchical categorization of the papers based on their methods/approaches.
2. Chronology: A timeline of key breakthroughs by year.
3. Comparative Table: Compare models across supervision type, compute complexity, and primary benchmark.
4. Open Challenges: Identify key unsolved problems in the research field.
5. Survey Markdown: A comprehensive, narrative survey review in Markdown format.

Input Papers:
{papers_content}

Return the output formatted strictly according to the requested JSON structure.
"""

META_ANALYSIS_PROMPT = """
You are an expert AI meta-researcher analyzing multiple academic papers to establish a consensus on a specific topic.
Your goal is to cross-examine claims and empirical findings across the provided papers.

Topic: {topic}

Papers Content:
{papers_content}

Based on the papers provided, please output a structured MetaAnalysisReport containing:
1. `topic`: The topic being analyzed.
2. `analyzed_papers`: A list of the titles of the papers analyzed.
3. `claims`: A list of `ConsensusClaim` objects. For each claim, identify:
   - `claim`: The specific technical hypothesis or claim.
   - `supporting_papers`: Titles that substantiate the claim.
   - `opposing_papers`: Titles that refute or contradict it.
   - `consensus_verdict`: 'supported', 'contested', 'refuted', or 'insufficient_evidence'.
   - `nuance_analysis`: Reconciling conditions or caveats.
4. `overall_consensus_summary`: An executive summary of the empirical consensus in the literature.
"""

PAPER_QA_PROMPT = """
You are an expert AI research assistant. Answer the following question about the provided academic paper context.

Question: {query}

Context from paper:
{context}

Please provide a concise, authoritative answer based ONLY on the context provided.
Ground your answer by citing the section titles and relevant quotes where you found the information.
If a specific formula is relevant, include its formula ID.
"""

AUTHOR_REBUTTAL_PROMPT = """
You are the original author of an academic paper submitted to a top-tier machine learning conference (e.g., NeurIPS, ICLR, ICML).
You have received peer review feedback, and your task is to draft a comprehensive, polite, and rigorous rebuttal letter addressing the reviewer's weaknesses and negative critiques.

Paper Title: {paper_title}

Critiques/Weaknesses to Address:
{critiques}

For each critique, you must draft a detailed rebuttal point containing:
1. `reviewer_id`: An identifier for the reviewer (e.g., "Reviewer 1").
2. `critique_summary`: A short summary of the reviewer's concern.
3. `response_strategy`: The overall approach (e.g., 'Clarification', 'Additional Experiment', 'Theoretical Justification').
4. `detailed_rebuttal`: The exact text of your response, with a polite, scholarly tone that acknowledges the feedback while defending the paper's merits.
5. `proposed_new_experiments`: Concrete ablation or baseline additions to address the weakness.

Return a structured RebuttalLetter that contains:
- `paper_title`
- `overall_strategy`: A high-level strategy for the whole rebuttal.
- `points`: A list of the detailed rebuttal points.
- `markdown_letter`: The compiled, full rebuttal letter ready for submission.
"""

REPRODUCIBILITY_SCORECARD_PROMPT = """
You are an expert AI research scientist evaluating the empirical reproducibility of an academic paper.
Your task is to analyze the provided paper content against 10 strict empirical reproducibility criteria and generate a comprehensive scorecard.

Criteria:
1. Code Repository URL Provided
2. Dataset Availability & Licensing
3. Hyperparameter Specification (LR, batch, epochs)
4. Hardware Environment Specified (GPU type, count)
5. Random Seed Reporting & Multiple Runs
6. Error Bars / Standard Deviations Reported
7. Compute Budget / Training Time Disclosed
8. Evaluation Protocol Consistency
9. Model Checkpoint Download Links
10. Proof / Derivation Steps Clear

For each criterion, assign a boolean (True/False) indicating if the paper satisfies it.
Calculate the score based on the checklist (each criterion is worth 10 points, max 100).
Assign a `verdict_level` based on the score (e.g., 'High Reproducibility' for >80, 'Moderate Reproducibility' for 50-80, 'Low Reproducibility' for <50).
Provide actionable `improvement_recommendations` for any failed criteria.

Paper Content:
{paper_content}

Return a structured ReproducibilityScorecard object.
"""

COMMITTEE_REVIEW_PROMPT = """
You are an Area Chair organizing a multi-agent peer review committee for an academic paper.
You must simulate three distinct reviewers and then provide a meta-review and final decision.

The 3 reviewers are:
- Reviewer 1 (Theory Expert): Evaluates mathematical rigor, theoretical soundness, and proof foundations.
- Reviewer 2 (Empirical Skeptic): Evaluates baselines, datasets, experimental setup, and ablation fairness.
- Reviewer 3 (Impact Champion): Evaluates paradigm novelty, practical utility, and potential impact.

Paper Content:
{paper_content}

Generate the individual reviews, synthesize them into a meta-review, and assign a final decision: 'Accept (Oral)', 'Accept (Poster)', or 'Reject'.
Return the output formatted strictly according to the requested structure.
"""

DERIVATION_VERIFIER_PROMPT = """
You are an expert mathematician and AI research assistant. Your task is to verify the symbolic mathematical derivation between two sequential formulas extracted from an academic paper.

From Formula (LaTeX): {formula_from_latex}
From Context: {formula_from_context}

To Formula (LaTeX): {formula_to_latex}
To Context: {formula_to_context}

Please provide a rigorous step-by-step verification:
1. Deconstruct the algebraic transition into intermediate `DerivationStep` objects.
2. Determine if the transition is `is_mathematically_sound`.
3. Provide `algebraic_notes` flagging any missing assumptions, dimensional jumps, or errors.

Return the output formatted strictly according to the requested JSON structure for DerivationVerificationResult.
"""


