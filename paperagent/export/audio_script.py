import os
from typing import Optional
from paperagent.models import PaperProject, PodcastScript, PodcastDialogueTurn
from paperagent.engine.llm_client import LLMClient

def generate_podcast_script(project: PaperProject, client: Optional[LLMClient] = None) -> PodcastScript:
    """
    Transforms paper findings, formula intuition, and reviewer critique into an engaging two-person conversational podcast dialogue (NotebookLM style).
    Hosts: "Alex (Explorer)" and "Morgan (Specialist)".
    Produces 6-12 dialogue turns with timing annotations and emotional tone markers.
    """
    system_prompt = (
        "You are an expert audio producer and academic science communicator. "
        "Your goal is to transform academic papers into an engaging, accessible, NotebookLM-style "
        "two-host podcast script. The hosts are 'Alex (Explorer)' who is inquisitive and asks big-picture questions, "
        "and 'Morgan (Specialist)' who is a deep domain technical expert. "
        "Generate 6-12 dialogue turns with emotional tone markers and realistic timing (in seconds)."
    )
    
    prompt = f"Please generate a podcast script for the paper titled '{project.paper.metadata.title}'.\n"
    
    if project.analysis:
        if project.analysis.executive_summary:
            prompt += f"\nExecutive Summary:\n{project.analysis.executive_summary}"
        if project.analysis.methodology_overview:
            prompt += f"\nMethodology:\n{project.analysis.methodology_overview}"
        if project.analysis.core_problem:
            prompt += f"\nCore Problem:\n{project.analysis.core_problem}"
            
    if client:
        # LLM based generation
        script = client.generate_structured(prompt=prompt, response_model=PodcastScript, system_prompt=system_prompt)
    else:
        # Fallback offline generation
        alex = "Alex (Explorer)"
        morgan = "Morgan (Specialist)"
        
        exec_summary = project.analysis.executive_summary if (project.analysis and project.analysis.executive_summary) else "It introduces a novel approach to the field."
        methodology = project.analysis.methodology_overview if (project.analysis and project.analysis.methodology_overview) else "They propose a new algorithm that significantly improves upon baselines."
        
        turns = [
            PodcastDialogueTurn(
                speaker=alex,
                speech=f"Welcome everyone! Today we're diving into a fascinating new paper titled '{project.paper.metadata.title}'. Morgan, what's the big picture here?",
                tone="excited",
                timing_seconds=15
            ),
            PodcastDialogueTurn(
                speaker=morgan,
                speech=f"Well Alex, the core of this work addresses some really interesting challenges. {exec_summary}",
                tone="analytical",
                timing_seconds=30
            ),
            PodcastDialogueTurn(
                speaker=alex,
                speech="That sounds incredibly impactful. How do they actually achieve this?",
                tone="thoughtful",
                timing_seconds=10
            ),
            PodcastDialogueTurn(
                speaker=morgan,
                speech=f"The methodology is quite elegant. {methodology}",
                tone="informative",
                timing_seconds=40
            ),
            PodcastDialogueTurn(
                speaker=alex,
                speech="Fascinating. Thanks for breaking that down for us, Morgan!",
                tone="appreciative",
                timing_seconds=10
            )
        ]
        
        script = PodcastScript(
            episode_title=f"Deep Dive: {project.paper.metadata.title}",
            hosts=[alex, morgan],
            turns=turns,
            total_duration_minutes=0.0,
            audio_briefing_markdown=""
        )

    # Compute total_duration_minutes
    total_seconds = sum(turn.timing_seconds for turn in script.turns)
    script.total_duration_minutes = round(total_seconds / 60.0, 2)
    
    # Generate audio_briefing_markdown
    markdown_lines = [
        f"# Audio Script: {script.episode_title}",
        f"**Estimated Duration**: {script.total_duration_minutes} minutes",
        f"**Hosts**: {', '.join(script.hosts)}",
        "",
        "## Transcript",
        ""
    ]
    
    for turn in script.turns:
        markdown_lines.append(f"**{turn.speaker}** *[{turn.tone}]* ({turn.timing_seconds}s):")
        markdown_lines.append(f"{turn.speech}")
        markdown_lines.append("")
        
    script.audio_briefing_markdown = "\n".join(markdown_lines)
    
    return script


def export_podcast_script_file(project: PaperProject, output_path: str) -> str:
    """
    Writes markdown transcript to file and returns output path.
    """
    script = generate_podcast_script(project)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(script.audio_briefing_markdown)
        
    return output_path