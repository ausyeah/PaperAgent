import json
from typing import Optional, List, Dict, Any
from paperagent.models import PaperProject, InteractiveNotebookBundle

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

def export_interactive_notebook(project: PaperProject, output_path: Optional[str] = None) -> InteractiveNotebookBundle:
    """
    Generates an advanced Jupyter notebook (.ipynb) with:
    - Mathematical Markdown cells with KaTeX equations.
    - Interactive ipywidgets sliders (e.g. sequence length, learning rate, temperature).
    - Live Matplotlib plots that update interactively based on slider inputs.
    - Synthesized core algorithm cells.
    Returns InteractiveNotebookBundle.
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
        
        # Interactive Widgets Cell
        widget_code = (
            "import ipywidgets as widgets\n"
            "from IPython.display import display\n"
            "import matplotlib.pyplot as plt\n"
            "import numpy as np\n\n"
            "def interactive_plot(sequence_length, learning_rate, temperature):\n"
            "    plt.figure(figsize=(10, 6))\n"
            "    x = np.linspace(0, sequence_length, 100)\n"
            "    y = np.sin(x * learning_rate) * np.exp(-x / temperature)\n"
            "    plt.plot(x, y)\n"
            "    plt.title(f'Interactive Visualization\\nseq_len={sequence_length}, lr={learning_rate:.4f}, temp={temperature}')\n"
            "    plt.grid(True)\n"
            "    plt.show()\n\n"
            "seq_len_slider = widgets.IntSlider(value=50, min=10, max=100, step=10, description='Sequence Length:')\n"
            "lr_slider = widgets.FloatLogSlider(value=0.01, base=10, min=-4, max=-1, step=0.5, description='Learning Rate:')\n"
            "temp_slider = widgets.FloatSlider(value=10.0, min=1.0, max=50.0, step=1.0, description='Temperature:')\n\n"
            "widgets.interactive(interactive_plot, sequence_length=seq_len_slider, learning_rate=lr_slider, temperature=temp_slider)\n"
        )
        cells.append(_create_markdown_cell("### Interactive Analysis"))
        cells.append(_create_code_cell(widget_code))
        

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

    widget_features = ["sequence_length_slider", "learning_rate_slider", "temperature_slider", "live_matplotlib_plot"]

    return InteractiveNotebookBundle(
        notebook_json=notebook_json,
        widget_features=widget_features,
        file_path=output_path
    )