import argparse
import sys
import os
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

# Try to import our app module for the 'serve' command
try:
    import uvicorn
except ImportError:
    uvicorn = None

# Mock functions representing the internal library
def mock_parse(source):
    return {
        "title": f"Mock Title for {source}",
        "authors": ["Alice Researcher", "Bob Scientist"],
        "abstract": "This is a mock abstract.",
        "sections": ["Introduction", "Methodology", "Experiments", "Conclusion"],
        "formula_count": 5
    }

def mock_analyze(source):
    return {
        "executive_brief": "This paper proposes a novel method.",
        "score": 7,
        "strengths": ["Novel approach", "Good empirical results"],
        "weaknesses": ["Missing baseline X", "Unproven claim Y"],
        "formula_explanations": [
            {
                "latex": "E=mc^2",
                "intuitive_intuition": "Energy and mass are interchangeable.",
                "variable_glossary": {"E": "Energy", "m": "mass", "c": "speed of light"}
            }
        ]
    }

def mock_synthesize(source):
    return "def mock_algorithm(x):\n    return x * 2\n\ndef test_mock():\n    assert mock_algorithm(2) == 4\n"

def main():
    parser = argparse.ArgumentParser(description="PaperAgent CLI - Academic paper deep-reader and code synthesizer.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: parse
    parse_parser = subparsers.add_parser("parse", help="Parse a paper and display metadata/outline")
    parse_parser.add_argument("source", help="ArXiv ID, URL, or Path to PDF")

    # Command: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Run deep analysis on a paper")
    analyze_parser.add_argument("source", help="ArXiv ID, URL, or Path to PDF")

    # Command: synthesize
    synth_parser = subparsers.add_parser("synthesize", help="Synthesize runnable code from paper algorithms")
    synth_parser.add_argument("source", help="ArXiv ID, URL, or Path to PDF")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Execute synthesized code in sandbox")
    run_parser.add_argument("source", help="ArXiv ID, URL, or Path to PDF")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Start the Web Dashboard API server")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host IP")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port number")

    args = parser.parse_args()
    console = Console()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "parse":
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console
        ) as progress:
            progress.add_task(description=f"Parsing paper from {args.source}...", total=None)
            import time; time.sleep(0.5) # Simulate work
            data = mock_parse(args.source)

        console.print(Panel(f"[bold blue]{data['title']}[/]\n[italic]{', '.join(data['authors'])}[/]", title="Paper Metadata"))

        table = Table(title="Paper Outline")
        table.add_column("Section", justify="left", style="cyan", no_wrap=True)
        table.add_column("Details", style="magenta")

        for idx, sec in enumerate(data['sections']):
            table.add_row(f"{idx+1}. {sec}", "...")
        table.add_row("Formulas Extracted", str(data['formula_count']))

        console.print(table)

    elif args.command == "analyze":
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console
        ) as progress:
            progress.add_task(description=f"Analyzing paper {args.source}...", total=None)
            import time; time.sleep(0.5)
            data = mock_analyze(args.source)

        score_color = "green" if data["score"] >= 7 else "yellow" if data["score"] >= 4 else "red"

        console.print(Panel(data["executive_brief"], title="Executive Brief", border_style="cyan"))

        critique_text = f"[bold {score_color}]Score: {data['score']}/10[/]\n\n"
        critique_text += "[bold]Strengths:[/]\n" + "\n".join(f"- {s}" for s in data['strengths']) + "\n\n"
        critique_text += "[bold]Weaknesses:[/]\n" + "\n".join(f"- {w}" for w in data['weaknesses'])

        console.print(Panel(critique_text, title="Reviewer Critique", border_style=score_color))

        if data.get("formula_explanations"):
            for idx, f in enumerate(data["formula_explanations"]):
                f_text = f"[bold cyan]Formula {idx+1}: {f['latex']}[/]\n\n"
                f_text += f"[bold]Intuition:[/] {f['intuitive_intuition']}\n\n"
                f_text += "[bold]Glossary:[/]\n" + "\n".join(f"- {k}: {v}" for k, v in f["variable_glossary"].items())
                console.print(Panel(f_text, title="Formula Explanation", border_style="blue"))

    elif args.command == "synthesize":
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=console
        ) as progress:
            progress.add_task(description=f"Synthesizing code for {args.source}...", total=None)
            import time; time.sleep(0.5)
            code = mock_synthesize(args.source)

        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Synthesized Code (Python)", border_style="green"))

    elif args.command == "run":
        console.print(f"[bold yellow]Executing synthesized code for {args.source}...[/]")
        code = mock_synthesize(args.source)

        with open("temp_cli_exec.py", "w") as f:
            f.write(code)
            f.write("\n\nif __name__ == '__main__':\n    test_mock()\n    print('Tests passed!')\n")

        try:
            result = subprocess.run(
                ["python", "temp_cli_exec.py"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                console.print(f"[bold green]Execution Successful! (Exit Code: {result.returncode})[/]")
            else:
                console.print(f"[bold red]Execution Failed! (Exit Code: {result.returncode})[/]")

            if result.stdout:
                console.print("[bold]STDOUT:[/]")
                console.print(result.stdout)
            if result.stderr:
                console.print("[bold]STDERR:[/]")
                console.print(result.stderr, style="red")

        except subprocess.TimeoutExpired:
            console.print("[bold red]Execution timed out after 5 seconds.[/]")
        finally:
            if os.path.exists("temp_cli_exec.py"):
                os.remove("temp_cli_exec.py")

    elif args.command == "serve":
        if uvicorn is None:
            console.print("[bold red]Error: uvicorn is not installed. Run `pip install uvicorn`.[/]")
            sys.exit(1)

        console.print(f"[bold green]Starting PaperAgent Web Dashboard on http://{args.host}:{args.port}[/]")
        uvicorn.run("paperagent.web.app:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()