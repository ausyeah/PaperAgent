import pytest
from paperagent.models import ParsedPaper, PaperMetadata
from paperagent.engine.survey import LiteratureSurveyEngine
from paperagent.engine.llm_client import LLMClient

@pytest.fixture
def mock_papers():
    return [
        ParsedPaper(
            metadata=PaperMetadata(title="BERT", authors=["Devlin"], year=2018, abstract="Bidirectional encoder."),
            raw_markdown="We present BERT."
        ),
        ParsedPaper(
            metadata=PaperMetadata(title="Attention Is All You Need", authors=["Vaswani"], year=2017, abstract="Transformers intro."),
            raw_markdown="We propose the Transformer."
        )
    ]

def test_survey_engine_fallback(mock_papers):
    engine = LiteratureSurveyEngine(llm_client=None)
    survey = engine.synthesize_literature_survey(topic="Transformers", papers=mock_papers)

    assert survey.topic == "Transformers"
    assert "Baseline Models" in survey.taxonomy_tree
    assert len(survey.taxonomy_tree["Baseline Models"]) == 2
    
    assert len(survey.chronology) == 2
    assert survey.chronology[0]["title"] == "Attention Is All You Need"
    assert survey.chronology[0]["year"] == 2017
    assert survey.chronology[1]["title"] == "BERT"
    assert survey.chronology[1]["year"] == 2018
    
    assert len(survey.comparative_table) == 2
    assert survey.comparative_table[0]["model"] == "Attention Is All You Need"
    assert survey.comparative_table[1]["model"] == "BERT"
    
    assert len(survey.open_challenges) > 0
    assert "Transformers" in survey.survey_markdown
    assert "Attention Is All You Need" in survey.survey_markdown

def test_survey_engine_with_mock_llm(mock_papers):
    client = LLMClient()
    # LLMClient handles mock internally when API keys are not set, parsing the schema for response_model
    engine = LiteratureSurveyEngine(llm_client=client)
    survey = engine.synthesize_literature_survey(topic="Transformers", papers=mock_papers)
    
    # Check that topic was preserved
    assert survey.topic == "Transformers"
    # Basic structural validations since actual mock content is pseudo-randomized by type
    assert isinstance(survey.taxonomy_tree, dict)
    assert isinstance(survey.chronology, list)
    assert isinstance(survey.comparative_table, list)
    assert isinstance(survey.open_challenges, list)
    assert isinstance(survey.survey_markdown, str)

def test_survey_engine_empty_papers():
    engine = LiteratureSurveyEngine()
    survey = engine.synthesize_literature_survey(topic="Empty Topic", papers=[])
    assert survey.topic == "Empty Topic"
    assert "No papers provided" in survey.survey_markdown