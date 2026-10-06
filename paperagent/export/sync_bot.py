import re
from typing import List
from paperagent.models import PaperProject, SyncBotBundle

def _sanitize_branch_name(title: str) -> str:
    """Creates a git-safe branch name from the paper title."""
    # Lowercase, replace non-alphanumerics with hyphens, remove multiple hyphens
    sanitized = re.sub(r'[^a-z0-9]', '-', title.lower())
    sanitized = re.sub(r'-+', '-', sanitized).strip('-')
    return f"repro/{sanitized}"

def create_reproduction_sync_bundle(project: PaperProject, target_repo: str = "org/repro") -> SyncBotBundle:
    """
    Constructs ready-to-use GitHub Pull Request content and automated git CLI commands
    for syncing a paper reproduction to a target repository.
    """
    paper_title = project.paper.metadata.title
    pr_title = f"Automated Reproduction: {paper_title}"
    
    # Extract details for body
    abstract = project.paper.metadata.abstract
    summary = ""
    if project.analysis:
        summary = project.analysis.executive_summary
    elif abstract:
        summary = abstract
        
    hardware_specs = "Unknown / Placeholder GPU" # From memory: incorporate hardware specs or constraints (using a placeholder if unavailable).
    
    # Determine test badge
    test_badge = "N/A"
    if project.synthesis and project.synthesis.execution_result:
        if project.synthesis.execution_result.success:
            test_badge = "✅ Tests Passed"
        else:
            test_badge = "❌ Tests Failed"

    # Build Markdown PR Body
    pr_body = f"""## Automated Reproduction: {paper_title}

### 📄 Summary
{summary}

### 🧪 Verification Status
**Status:** {test_badge}

### 💻 Hardware Specs
**Constraints/Requirements:** {hardware_specs}
"""
    
    # Determine branch name
    # Using project ID to ensure uniqueness or derived from title
    base_name = _sanitize_branch_name(paper_title)
    branch_name = f"{base_name}-{project.id[:8]}"
    
    # Generate Git Commands
    git_commands: List[str] = [
        f"git checkout -b {branch_name}",
        "git add .",
        f"git commit -m \"{pr_title}\"",
        f"git push -u origin {branch_name}",
        f"gh pr create --title \"{pr_title}\" --body-file .pr_body.md"
    ]
    
    return SyncBotBundle(
        target_repo=target_repo,
        pr_title=pr_title,
        pr_body=pr_body,
        git_commands=git_commands
    )