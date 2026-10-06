import os
from typing import List
from paperagent.models import PaperProject, SlideDeck

def generate_marp_slides(project: PaperProject) -> SlideDeck:
    """
    Generates clean, presentation-ready Marp markdown.
    """
    slides: List[str] = []

    # Frontmatter + Slide 1: Title Slide
    frontmatter = (
        "---\n"
        "marp: true\n"
        "theme: gaia\n"
        "paginate: true\n"
        "math: katex\n"
        "---\n\n"
    )
    authors = ", ".join(project.paper.metadata.authors) if project.paper.metadata.authors else "Unknown Authors"
    slide1 = (
        f"{frontmatter}"
        f"# {project.paper.metadata.title}\n\n"
        f"**{authors}**\n\n"
        "![PaperAgent Badge](https://img.shields.io/badge/Generated_by-PaperAgent-blue)\n"
    )
    slides.append(slide1)

    # Slide 2: Motivation & Executive Brief
    exec_summary = "Not available."
    if project.analysis and project.analysis.executive_summary:
        exec_summary = project.analysis.executive_summary

    slide2 = (
        "## Motivation & Executive Brief\n\n"
        f"{exec_summary}"
    )
    slides.append(slide2)

    # Slide 3: Core Mathematical Formulation
    math_content = "No mathematical formulation found."
    if project.analysis and project.analysis.formula_explanations:
        formula = project.analysis.formula_explanations[0]
        math_content = f"### Formula\n\n$$\n{formula.latex}\n$$\n\n**Intuition**: {formula.intuitive_intuition}"
    elif project.paper.sections:
        for sec in project.paper.sections:
            if sec.formulas:
                formula_obj = sec.formulas[0]
                math_content = f"### Formula\n\n$$\n{formula_obj.latex}\n$$\n"
                if formula_obj.plain_explanation:
                    math_content += f"\n**Explanation**: {formula_obj.plain_explanation}"
                break
    slide3 = (
        "## Core Mathematical Formulation\n\n"
        f"{math_content}"
    )
    slides.append(slide3)

    # Slide 4: Algorithmic Innovation & Pseudocode
    pseudocode = ""
    if project.paper.sections:
        for sec in project.paper.sections:
            if sec.algorithms:
                algo = sec.algorithms[0]
                pseudocode = f"```\n{algo.pseudocode}\n```\n"
                break

    innovation = "Not available."
    if project.analysis and project.analysis.methodology_overview:
        innovation = project.analysis.methodology_overview

    slide4 = (
        "## Algorithmic Innovation & Pseudocode\n\n"
        f"{pseudocode}\n"
        f"**Methodology**: {innovation}"
    )
    slides.append(slide4)

    # Slide 5: Python Reproduction Implementation
    code_content = "Code synthesis not available."
    if project.synthesis and project.synthesis.target_module_code:
        code_content = f"```python\n{project.synthesis.target_module_code}\n```"

    slide5 = (
        "## Python Reproduction Implementation\n\n"
        f"{code_content}"
    )
    slides.append(slide5)

    # Slide 6: NeurIPS Reviewer Critique
    critique_content = "Reviewer critique not available."
    if project.analysis and project.analysis.reviewer_critique:
        critique = project.analysis.reviewer_critique
        strengths = "\n".join([f"- {s}" for s in critique.strengths])
        weaknesses = "\n".join([f"- {w}" for w in critique.weaknesses])
        critique_content = (
            f"**Score**: {critique.score}/10\n\n"
            f"**Strengths**:\n{strengths}\n\n"
            f"**Weaknesses**:\n{weaknesses}"
        )
    slide6 = (
        "## NeurIPS Reviewer Critique\n\n"
        f"{critique_content}"
    )
    slides.append(slide6)

    # Slide 7: Conclusion & Key Takeaways
    conclusion = "Conclusion not available."
    if project.analysis and project.analysis.core_problem:
        conclusion = project.analysis.core_problem
    slide7 = (
        "## Conclusion & Key Takeaways\n\n"
        f"{conclusion}"
    )
    slides.append(slide7)

    marp_markdown = "\n\n---\n\n".join(slides)

    slide_count = marp_markdown.count("---") - 1

    return SlideDeck(
        title=project.paper.metadata.title,
        author="PaperAgent AI",
        marp_markdown=marp_markdown,
        slide_count=slide_count
    )

def export_slides_file(project: PaperProject, output_path: str) -> str:
    """
    Writes markdown to file and returns path.
    """
    deck = generate_marp_slides(project)

    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(deck.marp_markdown)

    return output_path
