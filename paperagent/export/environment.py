import os
import re
from pathlib import Path
from typing import Set

from paperagent.models import PaperProject, EnvironmentBundle

# A basic mapping of module names to package names.
PACKAGE_MAPPING = {
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
}

def extract_dependencies(code: str) -> Set[str]:
    """Extract standard import dependencies from Python code using regex."""
    deps = set()
    # Match `import foo` or `from foo import ...`
    # This regex captures the first level module name and allows leading whitespace.
    imports = re.findall(r'^\s*(?:from|import)\s+([a-zA-Z0-9_]+)', code, re.MULTILINE)
    
    # Common standard library modules to exclude
    stdlib = {
        "os", "sys", "re", "math", "time", "datetime", "json", "typing", 
        "collections", "itertools", "functools", "pathlib", "logging", "tempfile",
        "argparse", "subprocess", "warnings", "random", "io", "copy", "hashlib",
        "urllib", "sqlite3", "csv", "xml", "html", "unittest", "shutil",
        "socket", "multiprocessing", "threading", "asyncio", "dataclasses",
        "abc", "enum", "inspect", "ast", "contextlib", "glob", "platform",
        "base64", "zlib", "gzip", "tarfile", "zipfile", "traceback", "uuid"
    }

    for imp in imports:
        if imp not in stdlib and not imp.startswith("."):
            pkg = PACKAGE_MAPPING.get(imp, imp)
            deps.add(pkg)
            
    return deps

def generate_environment_bundle(project: PaperProject, python_version: str = "3.10", cuda_version: str = "12.1") -> EnvironmentBundle:
    """Analyzes synthesized code dependencies and generates hermetic reproduction environment bundle."""
    
    # Extract dependencies
    deps: Set[str] = set()
    if project.synthesis:
        if project.synthesis.target_module_code:
            deps.update(extract_dependencies(project.synthesis.target_module_code))
        if project.synthesis.test_suite_code:
            deps.update(extract_dependencies(project.synthesis.test_suite_code))
        if project.synthesis.toy_benchmark_code:
            deps.update(extract_dependencies(project.synthesis.toy_benchmark_code))
    
    # Ensure some standard testing dependencies if we have tests
    if project.synthesis and project.synthesis.test_suite_code:
        deps.add("pytest")

    paper_title = project.paper.metadata.title if project.paper and project.paper.metadata else "reproduction"
    
    # Safe project name for conda environment
    env_name = re.sub(r'[^a-zA-Z0-9_]', '_', paper_title.lower())
    if not env_name:
        env_name = "paperagent_env"
        
    deps_list = sorted(list(deps))
    
    # conda_yaml
    conda_deps_str = "\n".join(f"  - {d}" for d in deps_list)
    conda_yaml = f"""name: {env_name}
channels:
  - pytorch
  - nvidia
  - conda-forge
  - defaults
dependencies:
  - python={python_version}
{conda_deps_str}
"""

    # dockerfile_cuda
    dockerfile_cuda = f"""FROM nvidia/cuda:{cuda_version}.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    python3 \\
    python3-pip \\
    python3-dev \\
    git \\
    wget \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "reproduce.sh"]
"""

    # requirements_txt (pinned with compatible versions where known, otherwise unpinned)
    pinned_deps = []
    # Hardcode some typical scientific python versions as a best effort pin
    PINS = {
        "torch": ">=2.0.0",
        "numpy": ">=1.24.0",
        "scipy": ">=1.10.0",
        "scikit-learn": ">=1.2.0",
        "pandas": ">=2.0.0"
    }
    for dep in deps_list:
        if dep in PINS:
            pinned_deps.append(f"{dep}{PINS[dep]}")
        else:
            pinned_deps.append(dep)
            
    requirements_txt = "\n".join(pinned_deps) + "\n"
    
    # reproduction_script_sh
    reproduction_script_sh = """#!/bin/bash
set -e

echo "Starting Reproduction Suite..."

# Run Tests
if [ -f "test_reproduce.py" ]; then
    echo "Running Tests..."
    python -m pytest test_reproduce.py -v
fi

# Run Benchmark
if [ -f "reproduce.py" ]; then
    echo "Running Benchmark..."
    python reproduce.py
fi

echo "Reproduction Suite Completed."
"""

    # reproduction_script_ps1
    reproduction_script_ps1 = """$ErrorActionPreference = "Stop"

Write-Host "Starting Reproduction Suite..."

# Run Tests
if (Test-Path "test_reproduce.py") {
    Write-Host "Running Tests..."
    python -m pytest test_reproduce.py -v
}

# Run Benchmark
if (Test-Path "reproduce.py") {
    Write-Host "Running Benchmark..."
    python reproduce.py
}

Write-Host "Reproduction Suite Completed."
"""

    return EnvironmentBundle(
        paper_title=paper_title,
        conda_yaml=conda_yaml,
        dockerfile_cuda=dockerfile_cuda,
        requirements_txt=requirements_txt,
        reproduction_script_sh=reproduction_script_sh,
        reproduction_script_ps1=reproduction_script_ps1
    )


def export_environment_bundle(project: PaperProject, output_dir: str) -> str:
    """Writes all environment files into output_dir and returns directory path."""
    
    bundle = generate_environment_bundle(project)
    
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    (out_path / "environment.yml").write_text(bundle.conda_yaml, encoding="utf-8")
    (out_path / "Dockerfile").write_text(bundle.dockerfile_cuda, encoding="utf-8")
    (out_path / "requirements.txt").write_text(bundle.requirements_txt, encoding="utf-8")
    (out_path / "reproduce.sh").write_text(bundle.reproduction_script_sh, encoding="utf-8")
    (out_path / "reproduce.ps1").write_text(bundle.reproduction_script_ps1, encoding="utf-8")
    
    # Set executable permissions for shell script
    os.chmod(out_path / "reproduce.sh", 0o755)
    
    return str(out_path.absolute())