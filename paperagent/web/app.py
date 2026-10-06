import json
import subprocess
from datetime import datetime, timezone
from typing import Optional, Union, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
import os

from paperagent.models import (
    ParsedPaper,
    PaperMetadata,
    PaperSection,
    AnalysisReport,
    ReviewerCritique,
    FormulaExplanation,
    SynthesisResult,
    ExecutionResult
)

app = FastAPI(title="PaperAgent API", description="API for PaperAgent system")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ParseRequest(BaseModel):
    source: str

class ExecuteRequest(BaseModel):
    code: str

@app.post("/api/paper/parse", response_model=ParsedPaper)
async def parse_paper(
    source: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if not source and not file:
        raise HTTPException(status_code=400, detail="Must provide 'source' or 'file'")

    source_name = source if source else file.filename

    return ParsedPaper(
        metadata=PaperMetadata(
            title=f"Mock Title for {source_name}",
            authors=["Alice Researcher", "Bob Scientist"],
            abstract="This is a mock abstract of the paper. It explains the core concepts.",
            arxiv_id=source if source and "arxiv" in source.lower() else "1234.56789"
        ),
        sections=[
            PaperSection(title="Introduction", level=1, content="Mock introduction content."),
            PaperSection(title="Methodology", level=1, content="Mock methodology content.")
        ],
        raw_markdown=f"# Mock Title\n\n## Introduction\n\nContent...",
        source_type="arxiv" if source else "local_pdf"
    )

@app.post("/api/paper/analyze", response_model=AnalysisReport)
async def analyze_paper(paper: ParsedPaper):
    return AnalysisReport(
        executive_summary="This paper proposes a novel method for X.",
        core_problem="The problem of Y is difficult.",
        key_innovation="We introduce Z, which solves Y.",
        methodology_overview="We first do A, then B, then C.",
        formula_explanations=[
            FormulaExplanation(
                formula_id="eq-1",
                latex="E=mc^2",
                variable_glossary={"E": "Energy", "m": "mass", "c": "speed of light"},
                intuitive_intuition="Energy and mass are interchangeable.",
                step_by_step_breakdown=["Energy equals mass times the speed of light squared."]
            )
        ],
        reviewer_critique=ReviewerCritique(
            strengths=["Novel approach.", "Good empirical results."],
            weaknesses=["Missing baseline X.", "Unproven claim Y."],
            boundary_conditions=["Fails for large N."],
            potential_reproducibility_pitfalls=["Missing hyperparameters."],
            score=7
        )
    )

@app.post("/api/paper/synthesize", response_model=SynthesisResult)
async def synthesize_paper(paper: ParsedPaper):
    return SynthesisResult(
        algorithm_name="Mock Algorithm",
        target_module_code="def mock_algorithm(x):\n    return x * 2\n",
        test_suite_code="def test_mock_algorithm():\n    assert mock_algorithm(2) == 4\n",
        toy_benchmark_code="if __name__ == '__main__':\n    print(mock_algorithm(10))\n"
    )

import tempfile

@app.post("/api/paper/execute", response_model=ExecutionResult)
async def execute_code(req: ExecuteRequest):
    try:
        # Warning: For a real app, running arbitrary code is dangerous. This is a mock sandbox.
        fd, temp_path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, 'w') as f:
            f.write(req.code)

        start_time = datetime.now()
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        end_time = datetime.now()

        os.remove(temp_path)

        return ExecutionResult(
            success=result.returncode == 0,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time_seconds=(end_time - start_time).total_seconds()
        )
    except subprocess.TimeoutExpired:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return ExecutionResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr="Execution timed out.",
            execution_time_seconds=5.0
        )
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return ExecutionResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            execution_time_seconds=0.0
        )

from fastapi.responses import FileResponse, PlainTextResponse, Response

@app.get("/api/paper/export/markdown")
async def export_markdown():
    content = "# Exported Paper\n\nContent..."
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=\"report.md\""}
    )

@app.get("/api/paper/export/notebook")
async def export_notebook():
    notebook_json = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Exported Notebook\n"]
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5
    }
    return Response(
        content=json.dumps(notebook_json),
        media_type="application/x-ipynb+json",
        headers={"Content-Disposition": "attachment; filename=\"report.ipynb\""}
    )


static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
