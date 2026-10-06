import json
import logging
from typing import Optional

from paperagent.models import PaperProject, HuggingFaceAdapterResult
from paperagent.engine.llm_client import LLMClient

logger = logging.getLogger(__name__)

HF_ADAPTER_PROMPT = """
You are an expert machine learning engineer writing PyTorch and HuggingFace Transformers code.
Given the following self-contained PyTorch algorithm implementation, write an idiomatic HuggingFace wrapper.

The wrapper must include:
1. A subclass of `transformers.PretrainedConfig` (with the model hyperparameters).
2. A subclass of `transformers.PreTrainedModel` (with `config_class`, initialization, a `forward` method returning a standard `ModelOutput` or dict, and `.from_pretrained()` compatibility).

Original PyTorch Implementation:
```python
{source_code}
```

Provide the result as a JSON object adhering to the specified format. The 'adapter_module_code' must be self-contained (with all imports like `torch`, `transformers`) and not have markdown formatting. The 'example_usage_code' must show how to initialize the model from the config, save it using `save_pretrained`, and reload it using `from_pretrained`.
"""

def _get_fallback_hf_adapter() -> HuggingFaceAdapterResult:
    """Returns a realistic mock HuggingFace adapter when the LLM is offline or in mock mode."""
    adapter_code = '''
import torch
import torch.nn as nn
from transformers import PretrainedConfig, PreTrainedModel
from transformers.modeling_outputs import ModelOutput

class SynthesizedConfig(PretrainedConfig):
    model_type = "synthesized_model"
    
    def __init__(self, hidden_size=768, **kwargs):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size

class SynthesizedModel(PreTrainedModel):
    config_class = SynthesizedConfig
    
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.linear = nn.Linear(config.hidden_size, config.hidden_size)
        
    def forward(self, x, **kwargs):
        out = self.linear(x)
        return {"output": out}
'''
    usage_code = '''
from .hf_adapter import SynthesizedConfig, SynthesizedModel
import torch

config = SynthesizedConfig(hidden_size=128)
model = SynthesizedModel(config)

dummy_input = torch.randn(1, 128)
out = model(dummy_input)

model.save_pretrained("./test_hf_model")
loaded_model = SynthesizedModel.from_pretrained("./test_hf_model")
'''
    return HuggingFaceAdapterResult(
        model_class_name="SynthesizedModel",
        config_class_name="SynthesizedConfig",
        adapter_module_code=adapter_code.strip(),
        example_usage_code=usage_code.strip()
    )


def synthesize_hf_adapter(project: PaperProject, client: Optional[LLMClient] = None) -> HuggingFaceAdapterResult:
    """
    Takes synthesized PyTorch code and wraps it into idiomatic HuggingFace classes.
    """
    if project.synthesis is None or not project.synthesis.target_module_code:
        raise ValueError("PaperProject must have a synthesis result with target_module_code.")

    client = client or LLMClient()

    if not client.gemini_api_key and not client.openai_api_key:
        logger.info("No LLM API keys configured. Using fallback HuggingFaceAdapterResult.")
        return _get_fallback_hf_adapter()

    prompt = HF_ADAPTER_PROMPT.format(source_code=project.synthesis.target_module_code)
    
    try:
        result = client.generate_structured(
            prompt=prompt,
            response_model=HuggingFaceAdapterResult
        )
        return result
    except Exception as e:
        logger.error(f"Failed to generate HuggingFace adapter via LLM: {e}. Using fallback.")
        return _get_fallback_hf_adapter()
