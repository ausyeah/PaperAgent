import json
from typing import Optional, List, Dict, Any
from paperagent.models import PaperProject

def _create_markdown_cell(source: str) -> Dict[str, Any]:
    """Helper to create a markdown cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }

def _create_code_cell(source: str) -> Dict[str, Any]:
    """Helper to create a code cell."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    }

def export_jupyter_notebook(project: PaperProject, output_path: Optional[str] = None) -> str:
    """
    Constructs a valid Jupyter Notebook JSON string (.ipynb format v4).
    Includes markdown cells for paper introduction and formula breakdown,
    and code cells for the synthesized algorithm code, test suite, and runnable toy demo.
    Optionally writes to output_path.
    """
    cells: List[Dict[str, Any]] = []

    # Paper Introduction (Markdown)
    meta = project.paper.metadata
    intro_lines = [f"# {meta.title}"]
    if meta.authors:
        intro_lines.append(f"**Authors:** {', '.join(meta.authors)}")
    if meta.abstract:
        intro_lines.append(f"\n## Abstract\n{meta.abstract}")
    cells.append(_create_markdown_cell("\n".join(intro_lines)))

    # Formula Breakdown (Markdown)
    if project.analysis and project.analysis.formula_explanations:
        formula_lines = ["## Formula Demystification"]
        for f in project.analysis.formula_explanations:
            formula_lines.append(f"### Formula: {f.formula_id}")
            formula_lines.append(f"**LaTeX:**\n$${f.latex}$$")
            formula_lines.append(f"**Intuition:**\n{f.intuitive_intuition}\n")
        cells.append(_create_markdown_cell("\n".join(formula_lines)))

    # Code Synthesizer (Code cells)
    if project.synthesis:
        synth = project.synthesis
        cells.append(_create_markdown_cell(f"## Synthesized Algorithm: {synth.algorithm_name}\n\n### Algorithm Code"))
        cells.append(_create_code_cell(synth.target_module_code))

        cells.append(_create_markdown_cell("### Test Suite"))
        cells.append(_create_code_cell(synth.test_suite_code))

        if synth.toy_benchmark_code:
            cells.append(_create_markdown_cell("### Toy Benchmark Demo"))
            cells.append(_create_code_cell(synth.toy_benchmark_code))

    notebook = {
        "cells": cells,
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3",
                "mimetype": "text/x-python",
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    notebook_json = json.dumps(notebook, indent=2)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(notebook_json)

    return notebook_json
