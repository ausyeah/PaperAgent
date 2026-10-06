"""
PaperAgent Package Initialization
"""

__version__ = "0.6.0"
__author__ = "ausyeah"

from paperagent.models import (
    PaperMetadata,
    ExtractedFormula,
    ExtractedAlgorithm,
    PaperSection,
    ParsedPaper,
    AnalysisReport,
    SynthesisResult,
    PaperProject
)

__all__ = [
    "PaperMetadata",
    "ExtractedFormula",
    "ExtractedAlgorithm",
    "PaperSection",
    "ParsedPaper",
    "AnalysisReport",
    "SynthesisResult",
    "PaperProject",
]
