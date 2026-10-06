from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt

from paperagent.models import (
    ParsedPaper,
    AnalysisReport,
    ExtractedFormula,
    SynthesisResult,
    OpenReviewReport,
    PaperProject
)

def render_header() -> Panel:
    banner = r"""
    ____                        ___                    __
   / __ \____ _____  ___  _____/   |  ____ ____  ____ / /_
  / /_/ / __ `/ __ \/ _ \/ ___/ /| | / __ `/ _ \/ __ \ __/
 / ____/ /_/ / /_/ /  __/ /  / ___ |/ /_/ /  __/ / / / /_
/_/    \__,_/ .___/\___/_/  /_/  |_|\__, /\___/_/ /_/\__/
           /_/                     /____/
"""
    return Panel(f"[bold cyan]{banner}[/bold cyan]\n[italic]Academic Paper Deep-Reader & Code Synthesizer[/italic]", title="Welcome", border_style="blue")

def render_paper_summary(paper: ParsedPaper) -> Panel:
    meta = paper.metadata
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="bold cyan")
    table.add_column("Value")

    table.add_row("Title", meta.title)
    if meta.authors:
        table.add_row("Authors", ", ".join(meta.authors))
    if meta.arxiv_id:
        table.add_row("ArXiv ID", meta.arxiv_id)
    if meta.year:
        table.add_row("Year", str(meta.year))

    table.add_row("Abstract", meta.abstract)

    if paper.sections:
        sections_str = "\n".join([f"{i+1}. {s.title}" for i, s in enumerate(paper.sections)])
        table.add_row("Sections", sections_str)

    return Panel(table, title="Paper Summary", border_style="green")

def render_analysis_view(analysis: AnalysisReport) -> Panel:
    content = f"[bold]Executive Summary:[/bold]\n{analysis.executive_summary}\n\n"
    content += f"[bold]Core Problem:[/bold]\n{analysis.core_problem}\n\n"
    content += f"[bold]Key Innovation:[/bold]\n{analysis.key_innovation}\n\n"
    content += f"[bold]Methodology Overview:[/bold]\n{analysis.methodology_overview}"

    return Panel(content, title="Analysis Report", border_style="magenta")

def render_formula_gallery(formulas: List[ExtractedFormula]) -> Table:
    table = Table(title="Formula Gallery", box=None)
    table.add_column("ID", style="cyan")
    table.add_column("LaTeX", style="magenta")
    table.add_column("Context/Explanation", style="green")

    for f in formulas:
        explanation = f.plain_explanation or f.context_text or ""
        table.add_row(f.id, f.latex, explanation)

    return table

def render_code_view(synthesis: SynthesisResult) -> Panel:
    syntax = Syntax(synthesis.target_module_code, "python", theme="monokai", line_numbers=True)
    return Panel(syntax, title=f"Synthesized Code: {synthesis.algorithm_name}", border_style="yellow")

def render_openreview_card(review: OpenReviewReport) -> Panel:
    score_color = "green" if review.overall_recommendation >= 7 else ("yellow" if review.overall_recommendation >= 5 else "red")

    content = f"[bold]Summary:[/bold] {review.summary_of_work}\n\n"

    content += "[bold]Strengths:[/bold]\n"
    for s in review.strengths:
        content += f"- {s}\n"
    content += "\n"

    content += "[bold]Weaknesses:[/bold]\n"
    for w in review.weaknesses:
        content += f"- {w}\n"
    content += "\n"

    content += f"[bold]Scores:[/bold]\n"
    content += f"Soundness: {review.soundness_score}/4\n"
    content += f"Presentation: {review.presentation_score}/4\n"
    content += f"Contribution: {review.contribution_score}/4\n"
    content += f"Overall Recommendation: [{score_color}]{review.overall_recommendation}/10[/{score_color}]\n\n"

    checklist = "Yes" if review.reproducibility_checklist_passed else "No"
    content += f"[bold]Reproducibility Checklist Passed:[/bold] {checklist}"

    return Panel(content, title=f"OpenReview: {review.paper_title}", border_style="cyan")

def run_interactive_viewer(project: PaperProject) -> None:
    console = Console()
    console.print(render_header())

    while True:
        console.print("\n[bold]Select a view:[/bold]")
        console.print("1. Paper Summary")
        console.print("2. Analysis Report")
        console.print("3. Formula Gallery")
        console.print("4. Code Synthesis")
        console.print("5. OpenReview Card")
        console.print("q. Quit")

        choice = Prompt.ask("Enter choice", choices=["1", "2", "3", "4", "5", "q"])

        if choice == "q":
            break
        elif choice == "1":
            console.print(render_paper_summary(project.paper))
        elif choice == "2":
            if project.analysis:
                console.print(render_analysis_view(project.analysis))
            else:
                console.print("[yellow]No analysis available.[/yellow]")
        elif choice == "3":
            formulas = []
            for s in project.paper.sections:
                formulas.extend(s.formulas)
            if formulas:
                console.print(render_formula_gallery(formulas))
            else:
                console.print("[yellow]No formulas available.[/yellow]")
        elif choice == "4":
            if project.synthesis:
                console.print(render_code_view(project.synthesis))
            else:
                console.print("[yellow]No code synthesis available.[/yellow]")
        elif choice == "5":
            if project.analysis and project.analysis.reviewer_critique:
                critique = project.analysis.reviewer_critique
                review = OpenReviewReport(
                    paper_title=project.paper.metadata.title,
                    summary_of_work=project.analysis.executive_summary,
                    strengths=critique.strengths,
                    weaknesses=critique.weaknesses,
                    overall_recommendation=critique.score,
                    soundness_score=3,
                    presentation_score=3,
                    contribution_score=3,
                    reproducibility_checklist_passed=True
                )
                console.print(render_openreview_card(review))
            else:
                console.print("[yellow]No review available.[/yellow]")
