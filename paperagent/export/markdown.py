from paperagent.models import PaperProject

def export_markdown(project: PaperProject) -> str:
    """Exports a complete reading report as a Markdown string."""
    lines = []
    meta = project.paper.metadata

    # Paper metadata header
    lines.append(f"# {meta.title}")
    if meta.authors:
        lines.append(f"**Authors:** {', '.join(meta.authors)}")
    if meta.year:
        lines.append(f"**Year:** {meta.year}")
    if meta.arxiv_id:
        lines.append(f"**ArXiv ID:** {meta.arxiv_id}")
    if meta.doi:
        lines.append(f"**DOI:** {meta.doi}")
    if meta.categories:
        lines.append(f"**Categories:** {', '.join(meta.categories)}")
    if meta.pdf_url:
        lines.append(f"**PDF URL:** [{meta.pdf_url}]({meta.pdf_url})")

    lines.append("")
    if meta.abstract:
        lines.append(f"## Abstract\n{meta.abstract}\n")

    # Executive summary table
    if project.analysis:
        analysis = project.analysis
        lines.append("## Executive Summary")
        lines.append("| Metric | Overview |")
        lines.append("| --- | --- |")
        lines.append(f"| **Core Problem** | {analysis.core_problem.replace('|', '/')} |")
        lines.append(f"| **Key Innovation** | {analysis.key_innovation.replace('|', '/')} |")
        lines.append(f"| **Methodology** | {analysis.methodology_overview.replace('|', '/')} |")
        lines.append("")

        lines.append("### High-Level Summary")
        lines.append(f"{analysis.executive_summary}\n")

    # Section overview
    if project.paper.sections:
        lines.append("## Section Overview")
        for sec in project.paper.sections:
            lines.append(f"### {sec.title}")
            if sec.content:
                lines.append(f"{sec.content}\n")

    # Formula demystification cards with LaTeX
    if project.analysis and project.analysis.formula_explanations:
        lines.append("## Formula Demystification Cards")
        for f in project.analysis.formula_explanations:
            lines.append(f"### Formula: {f.formula_id}")
            lines.append(f"**LaTeX:**\n```latex\n{f.latex}\n```\n")
            lines.append(f"**Intuition:**\n{f.intuitive_intuition}\n")
            if f.variable_glossary:
                lines.append("**Glossary:**")
                for var, mean in f.variable_glossary.items():
                    lines.append(f"- `{var}`: {mean}")
                lines.append("")
            if f.step_by_step_breakdown:
                lines.append("**Step-by-step Breakdown:**")
                for i, step in enumerate(f.step_by_step_breakdown, 1):
                    lines.append(f"{i}. {step}")
                lines.append("")

    # NeurIPS Reviewer critique card
    if project.analysis and project.analysis.reviewer_critique:
        critique = project.analysis.reviewer_critique
        lines.append("## NeurIPS Reviewer Critique")
        lines.append(f"**Score:** {critique.score}/10\n")

        lines.append("### Strengths")
        for s in critique.strengths:
            lines.append(f"- {s}")
        lines.append("")

        lines.append("### Weaknesses")
        for w in critique.weaknesses:
            lines.append(f"- {w}")
        lines.append("")

        lines.append("### Boundary Conditions")
        for b in critique.boundary_conditions:
            lines.append(f"- {b}")
        lines.append("")

        lines.append("### Reproducibility Pitfalls")
        for p in critique.potential_reproducibility_pitfalls:
            lines.append(f"- {p}")
        lines.append("")

    # Synthesized Python code block
    if project.synthesis:
        synth = project.synthesis
        lines.append("## Synthesized Algorithm")
        lines.append(f"### {synth.algorithm_name}")
        lines.append("#### Algorithm Code")
        lines.append(f"```python\n{synth.target_module_code}\n```\n")
        lines.append("#### Test Suite")
        lines.append(f"```python\n{synth.test_suite_code}\n```\n")
        if synth.toy_benchmark_code:
            lines.append("#### Toy Benchmark")
            lines.append(f"```python\n{synth.toy_benchmark_code}\n```\n")

    return "\n".join(lines)
