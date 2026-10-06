import os
import zipfile
from paperagent.models import PaperProject
from .bibtex import generate_bibtex as generate_bibtex_meta

def generate_bibtex(project: PaperProject) -> str:
    """Generates valid BibTeX citation string for the project."""
    return generate_bibtex_meta(project.paper.metadata)

def generate_latex_source(project: PaperProject) -> str:
    """Generates a clean, compilable LaTeX document for the project."""

    # Extract metadata
    meta = project.paper.metadata
    title = meta.title or "Untitled Document"
    authors = ", ".join(meta.authors) if meta.authors else "Anonymous"
    abstract = meta.abstract or "No abstract provided."

    # Packages and preamble
    preamble = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{listings}
\usepackage{hyperref}
\usepackage{booktabs}

\title{""" + title + r"""}
\author{""" + authors + r"""}
\date{}

\begin{document}

\maketitle

\begin{abstract}
""" + abstract + r"""
\end{abstract}
"""

    sections = []

    # Executive Summary
    if project.analysis and project.analysis.executive_summary:
        sections.append(r"\section{Executive Summary}" + "\n\n" + project.analysis.executive_summary + "\n")

    # Mathematical Formulation
    if project.analysis and project.analysis.formula_explanations:
        sections.append(r"\section{Mathematical Formulation}")
        for formula in project.analysis.formula_explanations:
            sections.append(r"\subsection{Equation: " + formula.formula_id + r"}")
            sections.append(r"\begin{equation}")
            sections.append(formula.latex)
            sections.append(r"\end{equation}")

            sections.append(r"\textbf{Intuition:} " + formula.intuitive_intuition + "\n")

            if formula.variable_glossary:
                sections.append(r"\textbf{Glossary:}")
                sections.append(r"\begin{itemize}")
                for var, desc in formula.variable_glossary.items():
                    sections.append(rf"    \item ${var}$: {desc}")
                sections.append(r"\end{itemize}")
                sections.append("")

    # Extracted Algorithm
    if project.synthesis and project.synthesis.algorithm_name:
        sections.append(r"\section{Extracted Algorithm}")
        sections.append(r"Algorithm Name: " + project.synthesis.algorithm_name + "\n")

    # Python Implementation Code
    if project.synthesis and project.synthesis.target_module_code:
        sections.append(r"\section{Python Implementation Code}")
        sections.append(r"\begin{lstlisting}[language=Python]")
        sections.append(project.synthesis.target_module_code)
        sections.append(r"\end{lstlisting}" + "\n")

    # Peer Review
    if project.analysis and project.analysis.reviewer_critique:
        critique = project.analysis.reviewer_critique
        sections.append(r"\section{Peer Review}")
        sections.append(rf"\textbf{{Overall Score:}} {critique.score}/10" + "\n")

        if critique.strengths:
            sections.append(r"\subsection*{Strengths}")
            sections.append(r"\begin{itemize}")
            for item in critique.strengths:
                sections.append(rf"    \item {item}")
            sections.append(r"\end{itemize}")

        if critique.weaknesses:
            sections.append(r"\subsection*{Weaknesses}")
            sections.append(r"\begin{itemize}")
            for item in critique.weaknesses:
                sections.append(rf"    \item {item}")
            sections.append(r"\end{itemize}")

    # Conclusion
    footer = r"""
\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""

    body = "\n".join(sections)
    return preamble + body + footer


def export_latex_bundle(project: PaperProject, output_zip_path: str) -> str:
    """
    Creates a .zip archive containing:
      * main.tex: complete LaTeX source.
      * references.bib: BibTeX citations.
      * reproduction.py: synthesized Python code (if present).
      * README.md: Overleaf instructions & compilation guide.
    Returns the absolute path to the generated zip file.
    """
    main_tex = generate_latex_source(project)
    references_bib = generate_bibtex(project)

    readme_md = f"""# {project.paper.metadata.title or "LaTeX Export"}

## Overleaf Instructions
1. Upload this zip file to Overleaf as a new project.
2. The main compiler should be set to `pdfLaTeX`.
3. Compile the document.

## Contents
* `main.tex`: The main LaTeX document.
* `references.bib`: The BibTeX citation file.
"""

    reproduction_py = None
    if project.synthesis and project.synthesis.target_module_code:
        reproduction_py = project.synthesis.target_module_code
        readme_md += "* `reproduction.py`: The synthesized Python implementation of the algorithm.\n"

    abs_zip_path = os.path.abspath(output_zip_path)

    with zipfile.ZipFile(abs_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('main.tex', main_tex)
        zipf.writestr('references.bib', references_bib)
        zipf.writestr('README.md', readme_md)
        if reproduction_py:
            zipf.writestr('reproduction.py', reproduction_py)

    return abs_zip_path
