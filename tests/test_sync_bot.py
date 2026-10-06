import pytest
from datetime import datetime, timezone
from paperagent.models import (
    PaperProject, ParsedPaper, PaperMetadata, 
    AnalysisReport, ReviewerCritique, SynthesisResult, ExecutionResult
)
from paperagent.export import create_reproduction_sync_bundle


@pytest.fixture
def base_paper_metadata():
    return PaperMetadata(
        title="Attention Is All You Need",
        authors=["Vaswani et al."],
        abstract="We propose a new network architecture, the Transformer.",
        arxiv_id="1706.03762"
    )

@pytest.fixture
def mock_project_success(base_paper_metadata):
    paper = ParsedPaper(metadata=base_paper_metadata)
    analysis = AnalysisReport(
        executive_summary="Transformers changed everything.",
        core_problem="Sequence modeling without RNNs.",
        key_innovation="Self-attention.",
        methodology_overview="Multi-head attention blocks.",
        reviewer_critique=ReviewerCritique()
    )
    synthesis = SynthesisResult(
        algorithm_name="Transformer",
        target_module_code="def transformer(): pass",
        test_suite_code="def test(): pass",
        execution_result=ExecutionResult(success=True, exit_code=0)
    )
    return PaperProject(id="proj-success-1234", paper=paper, analysis=analysis, synthesis=synthesis)


@pytest.fixture
def mock_project_failure(base_paper_metadata):
    paper = ParsedPaper(metadata=base_paper_metadata)
    synthesis = SynthesisResult(
        algorithm_name="Transformer",
        target_module_code="def transformer(): pass",
        test_suite_code="def test(): pass",
        execution_result=ExecutionResult(success=False, exit_code=1)
    )
    return PaperProject(id="proj-fail-5678", paper=paper, analysis=None, synthesis=synthesis)


@pytest.fixture
def mock_project_no_synthesis(base_paper_metadata):
    paper = ParsedPaper(metadata=base_paper_metadata)
    return PaperProject(id="proj-none-9999", paper=paper)


def test_create_reproduction_sync_bundle_success(mock_project_success):
    bundle = create_reproduction_sync_bundle(mock_project_success, target_repo="test/org")
    
    assert bundle.target_repo == "test/org"
    assert bundle.pr_title == "Automated Reproduction: Attention Is All You Need"
    assert "Transformers changed everything." in bundle.pr_body
    assert "✅ Tests Passed" in bundle.pr_body
    
    # Check git commands
    assert len(bundle.git_commands) == 5
    assert bundle.git_commands[0] == "git checkout -b repro/attention-is-all-you-need-proj-suc"
    assert bundle.git_commands[1] == "git add ."
    assert bundle.git_commands[2] == 'git commit -m "Automated Reproduction: Attention Is All You Need"'
    assert bundle.git_commands[3] == "git push -u origin repro/attention-is-all-you-need-proj-suc"
    assert bundle.git_commands[4] == 'gh pr create --title "Automated Reproduction: Attention Is All You Need" --body-file .pr_body.md'


def test_create_reproduction_sync_bundle_failure(mock_project_failure):
    bundle = create_reproduction_sync_bundle(mock_project_failure)
    
    assert bundle.target_repo == "org/repro" # Default value
    assert "We propose a new network architecture, the Transformer." in bundle.pr_body # Abstract fallback
    assert "❌ Tests Failed" in bundle.pr_body


def test_create_reproduction_sync_bundle_no_synthesis(mock_project_no_synthesis):
    bundle = create_reproduction_sync_bundle(mock_project_no_synthesis)
    
    assert "N/A" in bundle.pr_body
    assert "Unknown / Placeholder GPU" in bundle.pr_body

    branch_cmd = bundle.git_commands[0]
    assert branch_cmd.startswith("git checkout -b repro/attention-is-all-you-need-proj-non")