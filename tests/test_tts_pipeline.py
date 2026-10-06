import pytest
import xml.etree.ElementTree as ET
import ast

from paperagent.models import PodcastScript, PodcastDialogueTurn
from paperagent.export.tts_pipeline import generate_ssml_podcast_bundle

def test_generate_ssml_podcast_bundle_xml_validity():
    script = PodcastScript(
        episode_title="Test Episode",
        turns=[
            PodcastDialogueTurn(speaker="Alex", speech="Hello!", tone="excited", timing_seconds=1),
            PodcastDialogueTurn(speaker="Morgan", speech="Welcome to the podcast.", tone="expert", timing_seconds=2),
        ]
    )
    
    bundle = generate_ssml_podcast_bundle(script)
    
    # Check that ssml_content is valid XML
    try:
        root = ET.fromstring(bundle.ssml_content)
    except ET.ParseError as e:
        pytest.fail(f"SSML is not valid XML: {e}")
        
    assert root.tag == "{http://www.w3.org/2001/10/synthesis}speak"

def test_phonetic_replacements_and_glossary():
    script = PodcastScript(
        episode_title="Math Episode",
        turns=[
            PodcastDialogueTurn(speaker="Alex", speech="The value of \\theta is calculated using \\mathcal{L}.", tone="curious", timing_seconds=0),
        ]
    )
    
    bundle = generate_ssml_podcast_bundle(script)
    
    # Check that \\theta and \\mathcal{L} are replaced
    assert "theta is calculated using loss function L" in bundle.ssml_content
    assert "\\theta" not in bundle.ssml_content
    assert "\\mathcal{L}" not in bundle.ssml_content
    
    # Check glossary
    assert r"\theta" in bundle.phonetic_glossary
    assert bundle.phonetic_glossary[r"\theta"] == "theta"
    assert r"\mathcal{L}" in bundle.phonetic_glossary
    assert bundle.phonetic_glossary[r"\mathcal{L}"] == "loss function L"

def test_voice_tag_alternation():
    script = PodcastScript(
        episode_title="Voice Episode",
        turns=[
            PodcastDialogueTurn(speaker="Alex", speech="One", tone="neutral", timing_seconds=0),
            PodcastDialogueTurn(speaker="Morgan", speech="Two", tone="neutral", timing_seconds=0),
            PodcastDialogueTurn(speaker="Alex", speech="Three", tone="neutral", timing_seconds=0),
            PodcastDialogueTurn(speaker="Jordan", speech="Four", tone="neutral", timing_seconds=0),
        ]
    )
    
    bundle = generate_ssml_podcast_bundle(script)
    
    root = ET.fromstring(bundle.ssml_content)
    voices = root.findall(".//voice", namespaces={'': 'http://www.w3.org/2001/10/synthesis'})
    
    assert len(voices) == 4
    
    # Check that same speaker gets the same voice
    alex_voice_1 = voices[0].attrib['name']
    morgan_voice = voices[1].attrib['name']
    alex_voice_2 = voices[2].attrib['name']
    jordan_voice = voices[3].attrib['name']
    
    assert alex_voice_1 == alex_voice_2
    assert alex_voice_1 != morgan_voice
    assert morgan_voice != jordan_voice
    assert alex_voice_1 != jordan_voice

def test_tts_script_py_is_valid_python():
    script = PodcastScript(
        episode_title="Code Episode",
        turns=[
            PodcastDialogueTurn(speaker="Alex", speech="Just some text.", tone="neutral", timing_seconds=0),
        ]
    )
    
    bundle = generate_ssml_podcast_bundle(script)
    
    try:
        ast.parse(bundle.tts_script_py)
    except SyntaxError as e:
        pytest.fail(f"Generated tts_script_py is not valid Python: {e}")