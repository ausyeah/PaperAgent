import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import BaseModel, Field
import httpx

from paperagent.engine.llm_client import LLMClient
from paperagent.config import settings

class DummyModel(BaseModel):
    name: str
    score: int
    is_active: bool

class NestedDummyModel(BaseModel):
    items: list[DummyModel]
    description: str

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")
    monkeypatch.setattr(settings, "openai_api_key", "")
    monkeypatch.setattr(settings, "default_model", "test-model")

def test_mock_mode_generate(mock_settings):
    client = LLMClient()
    res = client.generate("Hello")
    assert "mock response" in res

def test_mock_mode_generate_json(mock_settings):
    client = LLMClient()
    res = client.generate("Hello", json_mode=True)
    parsed = json.loads(res)
    assert parsed == {"mock": "response"}

def test_mock_mode_generate_structured(mock_settings):
    client = LLMClient()
    res = client.generate_structured("Hello", DummyModel)
    assert isinstance(res, DummyModel)
    assert res.name == "mock_string"
    assert res.score == 1
    assert res.is_active is True

def test_mock_mode_nested_generate_structured(mock_settings):
    client = LLMClient()
    res = client.generate_structured("Hello", NestedDummyModel)
    assert isinstance(res, NestedDummyModel)
    assert res.description == "mock_string"
    assert len(res.items) == 1
    assert isinstance(res.items[0], DummyModel)
    assert res.items[0].name == "mock_string"
    assert res.items[0].score == 1

@pytest.mark.asyncio
async def test_generate_gemini_success(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "fake-gemini-key")
    monkeypatch.setattr(settings, "openai_api_key", "")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Gemini response"}]}}]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        client = LLMClient()
        res = await client.generate_async("Hello")
        assert res == "Gemini response"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "generativelanguage.googleapis.com" in args[0]
        assert "fake-gemini-key" in args[0]

@pytest.mark.asyncio
async def test_generate_openai_success(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")
    monkeypatch.setattr(settings, "openai_api_key", "fake-openai-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "OpenAI response"}}]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        client = LLMClient()
        res = await client.generate_async("Hello")
        assert res == "OpenAI response"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "api.openai.com" in args[0]
        assert kwargs["headers"]["Authorization"] == "Bearer fake-openai-key"

@pytest.mark.asyncio
async def test_generate_retry_logic(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "fake-gemini-key")

    mock_error_response = MagicMock()
    mock_error_response.status_code = 429

    mock_success_response = MagicMock()
    mock_success_response.status_code = 200
    mock_success_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Success after retry"}]}}]
    }

    # We use a custom side_effect to raise an error first, then return success
    call_count = 0
    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.HTTPStatusError("Rate limited", request=MagicMock(), response=mock_error_response)
        return mock_success_response

    with patch("httpx.AsyncClient.post", side_effect=side_effect):
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            client = LLMClient()
            res = await client.generate_async("Hello")
            assert res == "Success after retry"
            assert call_count == 2
            mock_sleep.assert_called_once()

@pytest.mark.asyncio
async def test_generate_structured_success(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "fake-gemini-key")

    # Setup mock to return a valid JSON string for DummyModel
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": '{"name": "test", "score": 100, "is_active": true}'}]}}]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        client = LLMClient()
        res = await client.generate_structured_async("Hello", DummyModel)

        assert isinstance(res, DummyModel)
        assert res.name == "test"
        assert res.score == 100
        assert res.is_active is True

@pytest.mark.asyncio
async def test_generate_structured_failure(monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "fake-gemini-key")

    # Setup mock to return invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": 'invalid json'}]}}]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        client = LLMClient()
        with pytest.raises(ValueError, match="Failed to parse LLM output"):
            await client.generate_structured_async("Hello", DummyModel)
