import os
import requests

class LLMClient:
    """Client for communicating with LLM endpoints."""
    def __init__(self, api_key: str = None, endpoint: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.endpoint = endpoint or os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1/chat/completions")

    def generate(self, prompt: str, model: str = "gpt-4") -> str:
        """Generates a response using the LLM endpoint."""
        if not self.api_key:
            return "# Warning: No API key provided, returning mock response\n" + self._mock_generate(prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert software engineer and data scientist."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"# Error generating code: {str(e)}"

    def _mock_generate(self, prompt: str) -> str:
        if "test suite" in prompt.lower():
            return '''\
import pytest
import numpy as np

def test_shape_checks():
    assert True

def test_numerical_stability():
    assert True
'''
        elif "Momentum Contrast" in prompt:
            return '''\
import numpy as np

class MomentumContrast:
    def __init__(self, learning_rate: float = 0.01) -> None:
        self.learning_rate = learning_rate

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.zeros(X.shape[0])

if __name__ == '__main__':
    print("Demo")
'''
        else:
            return '''\
import numpy as np

class PaperAlgorithm:
    def __init__(self, learning_rate: float = 0.01) -> None:
        self.learning_rate = learning_rate

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.zeros(X.shape[0])

if __name__ == '__main__':
    print("Demo")
'''
