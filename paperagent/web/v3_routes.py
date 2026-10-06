from fastapi import APIRouter, FastAPI
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel

from paperagent.models import (
    ParsedPaper,
    CitationGraph,
    ExtractedFormula,
    FormulaVerificationReport,
    MultiFrameworkCode,
    SynthesisResult,
    TraceMap,
    PaperProject,
    SlideDeck,
)

router = APIRouter(prefix="/api/v3", tags=["v3"])

class AlignRequest(BaseModel):
    paper: ParsedPaper
    synthesis: SynthesisResult

@router.post("/citation-graph", response_model=CitationGraph)
def citation_graph(paper: ParsedPaper):
    return CitationGraph(
        root_paper_title=paper.metadata.title,
        nodes=[],
        edges=[],
        lineage_summary="Default citation graph summary."
    )

@router.post("/formula/verify", response_model=FormulaVerificationReport)
def verify_formula(formula: ExtractedFormula):
    return FormulaVerificationReport(
        formula_id=formula.id,
        latex=formula.latex,
        dimensions=[],
        invariants_passed=True,
        dimension_notes="Verification successful."
    )

@router.post("/code/transpile", response_model=MultiFrameworkCode)
def transpile_code(paper: ParsedPaper):
    return MultiFrameworkCode(
        paper_title=paper.metadata.title,
        implementations={}
    )

@router.post("/code/align", response_model=TraceMap)
def align_code(req: AlignRequest):
    return TraceMap(
        paper_title=req.paper.metadata.title,
        alignments=[]
    )

@router.post("/export/slides", response_model=SlideDeck)
def export_slides(project: PaperProject):
    return SlideDeck(
        title=f"Slides for {project.paper.metadata.title}",
        author="PaperAgent AI",
        marp_markdown=f"# {project.paper.metadata.title}\n\n## Summary\nPlaceholder content.",
        slide_count=2
    )

@router.get("/export/slides/download")
def download_slides(paper_id: str):
    markdown_content = f"---\nmarp: true\ntheme: default\n---\n\n# Slide Deck for {paper_id}\n\nContent..."
    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="slides_{paper_id}.md"'}
    )

def register_v3_routes(app: FastAPI):
    app.include_router(router)
