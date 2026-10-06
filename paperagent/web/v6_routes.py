"""
PaperAgent v0.6.0 REST API Routes
Autonomous AI Scientist & Self-Evolving Algorithm Lab
Exposes endpoints for hypothesis generation, self-debugging, gradient verification,
memory tracing, evolutionary architecture search, figure deconstruction, LaTeX math normalization,
cross-paper algorithm fusion, benchmark leaderboards, academic posters, ONNX/TensorRT export,
distributed DDP/FSDP launchers, paper semantic diffs, and experiment matrix sweeps.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from paperagent.models import (
    PaperProject,
    ParsedPaper,
    HypothesisCollection,
    SelfHealingResult,
    GradientVerificationReport,
    MemoryTraceProfile,
    EvolutionarySearchResult,
    FigureSemanticGraph,
    CanonicalMathExpression,
    MathNormalizationCollection,
    HybridSynthesisResult,
    LeaderboardSnapshot,
    AcademicPosterBundle,
    ONNXExportBundle,
    DistributedLaunchBundle,
    PaperSemanticDiff,
    ExperimentMatrixResult,
)
from paperagent.engine.hypothesis import ScientificHypothesisGenerator
from paperagent.runner.self_debugger import SelfHealingDebugger
from paperagent.engine.gradient_verifier import GradientVerifier
from paperagent.synthesizer.memory_tracer import MemoryTracer
from paperagent.engine.evolutionary_search import EvolutionaryArchitectureSearch
from paperagent.parser.figure_describer import FigureDeconstructor
from paperagent.parser.math_normalizer import MathNormalizer
from paperagent.engine.multi_paper_synthesizer import CrossPaperFusionSynthesizer
from paperagent.storage.leaderboard import LeaderboardTracker
from paperagent.export.poster import AcademicPosterGenerator
from paperagent.export.onnx_exporter import ONNXExportGenerator
from paperagent.synthesizer.distributed_launcher import DistributedLaunchGenerator
from paperagent.engine.semantic_diff import PaperSemanticDiffEngine
from paperagent.runner.experiment_runner import ExperimentMatrixRunner

router = APIRouter(prefix="/api/v6", tags=["v6"])


# --- Request Schemas ---

class HypothesisRequest(BaseModel):
    paper: ParsedPaper

class SelfHealRequest(BaseModel):
    code: str
    max_iterations: int = 3

class GradientVerifyRequest(BaseModel):
    code: str
    input_dim: int = 4
    epsilon: float = 1e-5

class MemoryTraceRequest(BaseModel):
    project: PaperProject

class EvolutionarySearchRequest(BaseModel):
    base_algorithm: str
    generations: int = 3
    population_size: int = 4

class FigureDeconstructRequest(BaseModel):
    figure_caption: str
    context_text: str = ""

class MathNormalizeRequest(BaseModel):
    latex_str: str

class PaperMathNormalizeRequest(BaseModel):
    paper: ParsedPaper

class FusePapersRequest(BaseModel):
    paper_a: ParsedPaper
    paper_b: ParsedPaper

class LeaderboardRequest(BaseModel):
    paper: ParsedPaper
    custom_benchmarks: Optional[Dict[str, float]] = None

class PosterRequest(BaseModel):
    project: PaperProject
    output_path: Optional[str] = None

class ONNXExportRequest(BaseModel):
    project: PaperProject
    opset_version: int = 17

class DistributedLaunchRequest(BaseModel):
    project: PaperProject
    world_size: int = 8

class SemanticDiffRequest(BaseModel):
    paper_v1: ParsedPaper
    paper_v2: ParsedPaper

class ExperimentMatrixRequest(BaseModel):
    matrix_name: str
    hparam_grid: Dict[str, List[Any]]
    seeds: List[int] = [42, 123]


# --- Endpoints ---

@router.post("/hypothesis", response_model=HypothesisCollection)
def generate_hypotheses(req: HypothesisRequest):
    generator = ScientificHypothesisGenerator()
    return generator.generate_hypotheses(req.paper)

@router.post("/self-heal", response_model=SelfHealingResult)
def heal_code(req: SelfHealRequest):
    debugger = SelfHealingDebugger()
    return debugger.heal_code(req.code, max_iterations=req.max_iterations)

@router.post("/gradient-verify", response_model=GradientVerificationReport)
def verify_gradients(req: GradientVerifyRequest):
    verifier = GradientVerifier()
    return verifier.verify_gradients(req.code, input_dim=req.input_dim, epsilon=req.epsilon)

@router.post("/memory-trace", response_model=MemoryTraceProfile)
def trace_memory(req: MemoryTraceRequest):
    tracer = MemoryTracer()
    return tracer.profile_memory(req.project)

@router.post("/evolutionary-search", response_model=EvolutionarySearchResult)
def search_architectures(req: EvolutionarySearchRequest):
    searcher = EvolutionaryArchitectureSearch()
    return searcher.search(req.base_algorithm, generations=req.generations, population_size=req.population_size)

@router.post("/deconstruct-figure", response_model=FigureSemanticGraph)
def deconstruct_figure(req: FigureDeconstructRequest):
    deconstructor = FigureDeconstructor()
    return deconstructor.deconstruct_figure(req.figure_caption, context_text=req.context_text)

@router.post("/normalize-math", response_model=CanonicalMathExpression)
def normalize_math(req: MathNormalizeRequest):
    normalizer = MathNormalizer()
    return normalizer.normalize_latex(req.latex_str)

@router.post("/normalize-paper-math", response_model=MathNormalizationCollection)
def normalize_paper_math(req: PaperMathNormalizeRequest):
    normalizer = MathNormalizer()
    return normalizer.normalize_paper_formulas(req.paper)

@router.post("/fuse-papers", response_model=HybridSynthesisResult)
def fuse_papers(req: FusePapersRequest):
    synthesizer = CrossPaperFusionSynthesizer()
    return synthesizer.fuse_papers(req.paper_a, req.paper_b)

@router.post("/leaderboard", response_model=LeaderboardSnapshot)
def track_leaderboard(req: LeaderboardRequest):
    tracker = LeaderboardTracker()
    return tracker.track_paper_performance(req.paper, custom_benchmarks=req.custom_benchmarks)

@router.post("/poster", response_model=AcademicPosterBundle)
def generate_poster(req: PosterRequest):
    generator = AcademicPosterGenerator()
    return generator.generate_poster(req.project, output_path=req.output_path)

@router.post("/onnx-export", response_model=ONNXExportBundle)
def export_onnx(req: ONNXExportRequest):
    generator = ONNXExportGenerator()
    return generator.generate_export_bundle(req.project, opset_version=req.opset_version)

@router.post("/distributed-launcher", response_model=DistributedLaunchBundle)
def generate_distributed_launcher(req: DistributedLaunchRequest):
    generator = DistributedLaunchGenerator()
    return generator.generate_distributed_bundle(req.project, world_size=req.world_size)

@router.post("/semantic-diff", response_model=PaperSemanticDiff)
def diff_papers(req: SemanticDiffRequest):
    engine = PaperSemanticDiffEngine()
    return engine.diff_papers(req.paper_v1, req.paper_v2)

@router.post("/experiment-matrix", response_model=ExperimentMatrixResult)
def run_experiment_matrix(req: ExperimentMatrixRequest):
    runner = ExperimentMatrixRunner()
    return runner.run_matrix(req.matrix_name, req.hparam_grid, seeds=req.seeds)

def register_v6_routes(app):
    app.include_router(router)
