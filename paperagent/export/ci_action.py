import os
import zipfile
import tempfile
import textwrap
from typing import Optional

from paperagent.models import PaperProject

def generate_github_workflow(project: PaperProject) -> str:
    """Generates valid YAML string for .github/workflows/reproduce.yml."""

    workflow_yaml = textwrap.dedent(f"""\
        name: Reproduce Algorithm

        "on":
          push:
            branches: [ "main", "master" ]
          workflow_dispatch:

        jobs:
          reproduce:
            runs-on: ubuntu-latest
            strategy:
              matrix:
                python-version: ["3.10", "3.11"]

            steps:
            - name: Checkout repository
              uses: actions/checkout@v4

            - name: Set up Python ${{{{ matrix.python-version }}}}
              uses: actions/setup-python@v5
              with:
                python-version: ${{{{ matrix.python-version }}}}

            - name: Install dependencies
              run: |
                python -m pip install --upgrade pip
                if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
                pip install pytest numpy torch

            - name: Run PyTest Suite
              run: |
                pytest test_reproduce.py -v

            - name: Run Benchmark Script
              run: |
                python reproduce.py
    """)
    return workflow_yaml

def export_reproduction_repo_bundle(project: PaperProject, output_zip_path: str) -> str:
    """
    Packages a standalone reproduction git repo archive as .zip.
    Returns the path to output zip.
    """
    if project.synthesis is None:
        raise ValueError("Cannot export reproduction bundle: PaperProject has no synthesis results.")

    workflow_yaml = generate_github_workflow(project)

    readme_md = textwrap.dedent(f"""\
        # Reproduction of: {project.paper.metadata.title}

        This repository contains the automatically synthesized reproduction of the algorithm presented in the paper.

        ## Files
        - `reproduce.py`: The core synthesized algorithm and benchmark/demo.
        - `test_reproduce.py`: The pytest verification suite.
        - `requirements.txt`: Dependencies.

        ## Usage
        1. Install dependencies:
           ```bash
           pip install -r requirements.txt
           ```
        2. Run tests:
           ```bash
           pytest test_reproduce.py
           ```
        3. Run algorithm demo:
           ```bash
           python reproduce.py
           ```
    """)

    requirements_txt = "pytest\nnumpy\ntorch\n"

    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(".github/workflows/reproduce.yml", workflow_yaml)
        zipf.writestr("reproduce.py", project.synthesis.target_module_code)
        zipf.writestr("test_reproduce.py", project.synthesis.test_suite_code)
        zipf.writestr("requirements.txt", requirements_txt)
        zipf.writestr("README.md", readme_md)

    return output_zip_path
