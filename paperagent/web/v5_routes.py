"""
PaperAgent v0.5.0 REST API Routes
Exposes endpoints for Triton GPU kernels, Peer review committees, Interactive citation graphs,
Synthetic dataset fixtures, Precision quantizers, Reproducibility scorecards, Table extractors,
Git/Overleaf sync bots, Mathematical derivation verifiers, SSML podcast bundles,
Semantic library clustering, Interactive notebooks, Seminal paper benchmarks, and Speedup comparators.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from paperagent.models import (
    PaperProject,
    ParsedPaper,
    TritonKernelResult,
    CommitteeReview,
    GraphVisualizationBundle,
    SyntheticDatasetFixture,
    QuantizationProfile,
    ReproducibilityScorecard,
    ExtractedTableCollection,
    SyncBotBundle,
    DerivationVerificationResult,
    SSMLPodcastBundle,
    TopicClusterCollection,
    InteractiveNotebookBundle,
    BenchmarkEvaluationResult,
    SpeedupComparisonResult,
    CitationGraph,
    PodcastScript,
    StoredPaperRecord,
)
from paperagent.synthesizer.kernel import TritonKernelSynthesizer
from paperagent.engine.committee import PeerReviewCommittee
from paperagent.export.graph_view import export_citation_graph_html
from paperagent.synthesizer.dataset_gen import SyntheticDatasetGenerator
from paperagent.synthesizer.quantizer import PrecisionQuantizer
from paperagent.engine.scorecard import ReproducibilityEvaluator
from paperagent.parser.table_extractor import TableExtractor
from paperagent.export.sync_bot import create_reproduction_sync_bundle
from paperagent.engine.derivation import DerivationVerifier
from paperagent.export.tts_pipeline import generate_ssml_podcast_bundle
from paperagent.storage.clusterer import PaperLibraryClusterer
from paperagent.export.interactive_notebook import export_interactive_notebook
from paperagent.benchmarks.reproduce_papers import PaperReproductionBenchmark
from paperagent.engine.speedup_comparator import SpeedupComparator

router = APIRouter(prefix="/api/v5", tags=["v5"])


# --- Request Schemas ---

class KernelRequest(BaseModel):
    project: PaperProject
    operation_name: Optional[str] = "flash_attention"

class CommitteeRequest(BaseModel):
    paper: ParsedPaper

class GraphViewRequest(BaseModel):
    graph: CitationGraph

class DatasetFixtureRequest(BaseModel):
    project: PaperProject
    num_samples: int = 1000

class QuantizeRequest(BaseModel):
    project: PaperProject

class ScorecardRequest(BaseModel):
    paper: ParsedPaper

class TableExtractRequest(BaseModel):
    paper: ParsedPaper

class SyncBotRequest(BaseModel):
    project: PaperProject
    target_repo: Optional[str] = None

class DerivationRequest(BaseModel):
    formula_from_id: str
    formula_from_latex: str
    formula_from_context: str
    formula_to_id: str
    formula_to_latex: str
    formula_to_context: str

class SSMLPodcastRequest(BaseModel):
    podcast: PodcastScript

class ClusterRequest(BaseModel):
    papers: List[StoredPaperRecord]
    k_clusters: int = 3

class InteractiveNotebookRequest(BaseModel):
    project: PaperProject

class BenchmarkRequest(BaseModel):
    paper_name: str
    code: str

class SpeedupRequest(BaseModel):
    algorithm_name: str
    input_shape: tuple = (16, 512, 64)


# --- Endpoints ---

@router.post("/kernel", response_model=TritonKernelResult)
def synthesize_kernel(req: KernelRequest):
    synthesizer = TritonKernelSynthesizer()
    return synthesizer.synthesize_triton_kernel(req.project)

@router.post("/committee", response_model=CommitteeReview)
def run_committee_review(req: CommitteeRequest):
    committee = PeerReviewCommittee()
    return committee.evaluate_paper_committee(req.paper)

@router.post("/graph-view", response_model=GraphVisualizationBundle)
def generate_graph_view(req: GraphViewRequest):
    return export_citation_graph_html(req.graph)

@router.post("/dataset-fixture", response_model=SyntheticDatasetFixture)
def generate_dataset_fixture(req: DatasetFixtureRequest):
    generator = SyntheticDatasetGenerator()
    return generator.generate_dataset_fixture(req.project, num_samples=req.num_samples)

@router.post("/quantize", response_model=QuantizationProfile)
def profile_quantization(req: QuantizeRequest):
    quantizer = PrecisionQuantizer()
    return quantizer.profile_quantization(req.project)

@router.post("/scorecard", response_model=ReproducibilityScorecard)
def evaluate_scorecard(req: ScorecardRequest):
    evaluator = ReproducibilityEvaluator()
    return evaluator.evaluate_reproducibility(req.paper)

@router.post("/extract-tables", response_model=ExtractedTableCollection)
def extract_tables(req: TableExtractRequest):
    extractor = TableExtractor()
    return extractor.extract_tables(req.paper)

@router.post("/sync-bot", response_model=SyncBotBundle)
def generate_sync_bot(req: SyncBotRequest):
    return create_reproduction_sync_bundle(req.project, target_repo=req.target_repo)

@router.post("/derivation", response_model=DerivationVerificationResult)
def verify_derivation(req: DerivationRequest):
    verifier = DerivationVerifier()
    from paperagent.models import ExtractedFormula
    f_from = ExtractedFormula(
        id=req.formula_from_id,
        latex=req.formula_from_latex,
        plain_explanation=req.formula_from_context,
    )
    f_to = ExtractedFormula(
        id=req.formula_to_id,
        latex=req.formula_to_latex,
        plain_explanation=req.formula_to_context,
    )
    return verifier.verify_derivation_steps(f_from, f_to)

@router.post("/tts-ssml", response_model=SSMLPodcastBundle)
def generate_tts_ssml(req: SSMLPodcastRequest):
    return generate_ssml_podcast_bundle(req.podcast)

@router.post("/cluster", response_model=TopicClusterCollection)
def cluster_papers(req: ClusterRequest):
    clusterer = PaperLibraryClusterer()
    return clusterer.cluster_papers(req.papers, num_clusters=req.k_clusters)

@router.post("/interactive-notebook", response_model=InteractiveNotebookBundle)
def generate_notebook(req: InteractiveNotebookRequest):
    return export_interactive_notebook(req.project)

@router.post("/benchmark-reproduce", response_model=BenchmarkEvaluationResult)
def run_benchmark_reproduce(req: BenchmarkRequest):
    runner = PaperReproductionBenchmark()
    return runner.benchmark_paper_reproduction(paper_name=req.paper_name, code=req.code)

@router.post("/speedup", response_model=SpeedupComparisonResult)
def compare_speedup(req: SpeedupRequest):
    comparator = SpeedupComparator()
    return comparator.compare_framework_runtimes(
        algorithm_name=req.algorithm_name,
        input_shape=req.input_shape
    )

def register_v5_routes(app):
    app.include_router(router)

