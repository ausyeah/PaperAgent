import re
import xml.sax.saxutils as saxutils
from typing import Dict, List, Tuple
from paperagent.models import PodcastScript, SSMLPodcastBundle

PHONETIC_MAP = {
    r"\\theta": "theta",
    r"\\mathcal\{L\}": "loss function L",
    r"\\alpha": "alpha",
    r"\\beta": "beta",
    r"\\gamma": "gamma",
    r"\\lambda": "lambda",
    r"\\mu": "mu",
    r"\\sigma": "sigma",
    r"\\Omega": "omega",
    r"\\Delta": "delta",
    r"\\epsilon": "epsilon",
    r"\\nabla": "nabla",
    r"\\sum": "summation",
    r"\\int": "integral",
    r"\\prod": "product",
    r"\\infty": "infinity",
    r"\\pm": "plus or minus",
    r"\\approx": "approximately equal to",
    r"\\neq": "not equal to",
    r"\\leq": "less than or equal to",
    r"\\geq": "greater than or equal to",
    r"\^2": "squared",
    r"\^3": "cubed",
    r"_\{i\}": "sub i",
    r"_\{j\}": "sub j",
}

AVAILABLE_VOICES = [
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-US-AriaNeural",
    "en-US-DavisNeural"
]

def generate_ssml_podcast_bundle(script: PodcastScript) -> SSMLPodcastBundle:
    """
    Converts a PodcastScript into an SSMLPodcastBundle.
    """
    glossary: Dict[str, str] = {}
    ssml_lines: List[str] = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">']
    
    # Assign voices to speakers
    speaker_voices: Dict[str, str] = {}
    voice_idx = 0
    
    for turn in script.turns:
        if turn.speaker not in speaker_voices:
            speaker_voices[turn.speaker] = AVAILABLE_VOICES[voice_idx % len(AVAILABLE_VOICES)]
            voice_idx += 1
            
        voice = speaker_voices[turn.speaker]
        
        # Apply phonetic replacements
        speech_text = turn.speech
        for latex, phonetic in PHONETIC_MAP.items():
            if re.search(latex, speech_text):
                speech_text = re.sub(latex, phonetic, speech_text)
                # Ensure the latex key without escape characters is in glossary
                clean_latex = latex.replace("\\\\", "\\").replace("\\{", "{").replace("\\}", "}")
                if clean_latex.startswith("\\") and "\\" in latex:
                   glossary[clean_latex] = phonetic
                else:
                   glossary[latex] = phonetic
                   
        
        # Escape for XML
        speech_text = saxutils.escape(speech_text)
        
        # Construct SSML tags for the turn
        ssml_turn = f'  <voice name="{voice}">'
        
        # Tone
        # Some simple prosody mappings based on tone
        rate = "medium"
        pitch = "medium"
        if "excited" in turn.tone.lower() or "curious" in turn.tone.lower():
            rate = "fast"
            pitch = "high"
        elif "serious" in turn.tone.lower() or "expert" in turn.tone.lower():
            rate = "slow"
            pitch = "low"
            
        ssml_turn += f'<prosody rate="{rate}" pitch="{pitch}">'
        ssml_turn += speech_text
        
        # Break for timing
        if turn.timing_seconds > 0:
            # max allowed in some engines might be 10s, but we'll use ms
            break_ms = turn.timing_seconds * 1000
            ssml_turn += f' <break time="{break_ms}ms"/>'
            
        ssml_turn += '</prosody>'
        ssml_turn += '</voice>'
        
        ssml_lines.append(ssml_turn)
        
    ssml_lines.append('</speak>')
    ssml_content = "\n".join(ssml_lines)
    
    # Generate standalone TTS Python script
    # Use repr() to safely embed the multi-line string in the python script.
    tts_script_py = f'''import sys
import subprocess
import os

SSML_CONTENT = {repr(ssml_content)}

def render_edge_tts(output_file="podcast.mp3"):
    # Save SSML to a temporary file
    temp_ssml = "temp_podcast.ssml"
    with open(temp_ssml, "w", encoding="utf-8") as f:
        f.write(SSML_CONTENT)
    
    try:
        print(f"Running edge-tts to generate {{output_file}}...")
        subprocess.run(["edge-tts", "--ssml", temp_ssml, "--write-media", output_file], check=True)
        print("Success!")
    except FileNotFoundError:
        print("edge-tts not found. Falling back to pyttsx3.")
        render_pyttsx3(output_file)
    except subprocess.CalledProcessError as e:
        print(f"edge-tts failed: {{e}}")
    finally:
        if os.path.exists(temp_ssml):
            os.remove(temp_ssml)

def render_pyttsx3(output_file="podcast.mp3"):
    try:
        import pyttsx3
        import re
        
        print("Initializing pyttsx3...")
        engine = pyttsx3.init()
        
        # Strip XML tags for basic pyttsx3 fallback
        text_only = re.sub(r'<[^>]+>', ' ', SSML_CONTENT)
        text_only = " ".join(text_only.split())
        
        # pyttsx3 save_to_file often works with .wav or .mp3 depending on OS
        engine.save_to_file(text_only, output_file)
        engine.runAndWait()
        print(f"Saved audio using pyttsx3 to {{output_file}}")
    except ImportError:
        print("pyttsx3 not installed. Please install edge-tts or pyttsx3.")

if __name__ == "__main__":
    render_edge_tts()
'''

    return SSMLPodcastBundle(
        episode_title=script.episode_title,
        ssml_content=ssml_content,
        tts_script_py=tts_script_py,
        phonetic_glossary=glossary
    )