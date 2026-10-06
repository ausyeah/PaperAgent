import json
import asyncio
import logging
from typing import Optional, Type, Dict, Any, TypeVar
from pydantic import BaseModel
import httpx

from paperagent.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key
        self.openai_api_key = settings.openai_api_key
        self.default_model = settings.default_model

    def _get_mock_response(self, json_mode: bool, response_model: Optional[Type[BaseModel]] = None) -> str:
        if response_model:
            schema = response_model.model_json_schema()
            mock_data = self._generate_mock_from_schema(schema)
            return json.dumps(mock_data)
        elif json_mode:
            return '{"mock": "response"}'
        else:
            return "This is a mock response because no API keys are configured."

    def _generate_mock_from_schema(self, schema: Dict[str, Any], defs: Optional[Dict[str, Any]] = None) -> Any:
        if defs is None:
            defs = schema.get("$defs", {})

        # Handle references to other schemas if present (e.g. from $defs)
        if "$ref" in schema:
            ref_path = schema["$ref"]
            if ref_path.startswith("#/$defs/"):
                ref_name = ref_path.split("/")[-1]
                if ref_name in defs:
                    return self._generate_mock_from_schema(defs[ref_name], defs)
            return {} # Fallback

        if "type" not in schema:
            if "properties" in schema:
                schema["type"] = "object"
            elif "anyOf" in schema:
                return self._generate_mock_from_schema(schema["anyOf"][0], defs)
            elif "allOf" in schema:
                return self._generate_mock_from_schema(schema["allOf"][0], defs)
            else:
                return "mock_string"

        t = schema["type"]
        if t == "object":
            obj = {}
            for prop, prop_schema in schema.get("properties", {}).items():
                obj[prop] = self._generate_mock_from_schema(prop_schema, defs)
            return obj
        elif t == "array":
            item_schema = schema.get("items", {})
            return [self._generate_mock_from_schema(item_schema, defs)]
        elif t == "string":
            return "mock_string"
        elif t == "integer":
            return 1
        elif t == "number":
            return 1.0
        elif t == "boolean":
            return True
        else:
            return "mock_value"

    async def _generate_gemini(self, prompt: str, system_prompt: Optional[str], json_mode: bool, temperature: float, client: httpx.AsyncClient) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.default_model}:generateContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": settings.max_tokens,
            }
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini response: {data}")
            raise ValueError("Invalid response format from Gemini API") from e

    async def _generate_openai(self, prompt: str, system_prompt: Optional[str], json_mode: bool, temperature: float, client: httpx.AsyncClient) -> str:
        # Assuming typical OpenAI-compatible endpoint, standard url could be from env or default
        url = "https://api.openai.com/v1/chat/completions" # Defaulting to standard OpenAI if not specified elsewhere
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": settings.max_tokens
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse OpenAI response: {data}")
            raise ValueError("Invalid response format from OpenAI API") from e

    async def generate_async(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False, temperature: float = 0.2) -> str:
        if not self.gemini_api_key and not self.openai_api_key:
            return self._get_mock_response(json_mode)

        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    if self.gemini_api_key:
                        return await self._generate_gemini(prompt, system_prompt, json_mode, temperature, client)
                    elif self.openai_api_key:
                        return await self._generate_openai(prompt, system_prompt, json_mode, temperature, client)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limited. Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                    else:
                        raise e
                else:
                    raise e
            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Network error: {e}. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise e

        raise Exception("Max retries exceeded")

    def generate(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False, temperature: float = 0.2) -> str:
        return asyncio.run(self.generate_async(prompt, system_prompt, json_mode, temperature))

    async def generate_structured_async(self, prompt: str, response_model: Type[T], system_prompt: Optional[str] = None) -> T:
        if not self.gemini_api_key and not self.openai_api_key:
            mock_str = self._get_mock_response(json_mode=True, response_model=response_model)
            return response_model.model_validate_json(mock_str)

        # Enhance system prompt to output matching JSON schema
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)

        enhanced_system_prompt = system_prompt or ""
        enhanced_system_prompt += f"\n\nYou MUST return the response strictly as a JSON object that adheres to the following JSON schema:\n{schema_str}"

        # Generate using json mode
        response_text = await self.generate_async(
            prompt=prompt,
            system_prompt=enhanced_system_prompt,
            json_mode=True
        )

        try:
            return response_model.model_validate_json(response_text)
        except Exception as e:
            logger.error(f"Failed to parse structured output. Raw response: {response_text}")
            raise ValueError(f"Failed to parse LLM output into {response_model.__name__}") from e

    def generate_structured(self, prompt: str, response_model: Type[T], system_prompt: Optional[str] = None) -> T:
        return asyncio.run(self.generate_structured_async(prompt, response_model, system_prompt))
