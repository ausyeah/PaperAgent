import re
import logging
from typing import Optional, List, Dict
from paperagent.models import FigureSemanticGraph, FigureNode, FigureEdge
from paperagent.engine.llm_client import LLMClient

logger = logging.getLogger(__name__)

FIGURE_DECONSTRUCTOR_PROMPT = """
You are an expert AI architect. Your task is to deconstruct an academic architecture description or figure caption into a computational directed acyclic graph (DAG) and synthesize a corresponding Python code stub.

Figure Caption:
{figure_caption}

Context Text:
{context_text}

Extract the nodes (`FigureNode`), directed dataflow edges (`FigureEdge`), and a `synthesized_code_stub` (in Python using PyTorch nn.Module) that matches the graph. 
Nodes typically represent operators or layers (e.g. Convolution, Attention, Linear).
Edges represent the flow of tensors between these operators.
Return a complete JSON representation of a FigureSemanticGraph.
"""

class FigureDeconstructor:
    """Deconstructs academic architecture diagram descriptions into a semantic DAG."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.client = llm_client or LLMClient()
        
    def deconstruct_figure(self, figure_caption: str, context_text: str = "") -> FigureSemanticGraph:
        """
        Parses architectural descriptions and figure captions into a DAG.
        Uses LLM with a deterministic regex/heuristic fallback.
        """
        prompt = FIGURE_DECONSTRUCTOR_PROMPT.format(
            figure_caption=figure_caption,
            context_text=context_text
        )
        
        try:
            graph = self.client.generate_structured(
                prompt=prompt,
                response_model=FigureSemanticGraph,
                system_prompt="You are an expert AI architect."
            )
            # Ensure figure_id is set
            if not graph.figure_id:
                graph.figure_id = "extracted-figure"
            return graph
        except Exception as e:
            logger.warning(f"LLM figure deconstruction failed: {e}. Falling back to deterministic heuristics.")
            return self._fallback_deconstruct(figure_caption, context_text)
            
    def _fallback_deconstruct(self, caption: str, context: str) -> FigureSemanticGraph:
        """
        Deterministic regex/heuristic fallback for offline execution.
        """
        text = caption + " " + context
        text_lower = text.lower()
        
        nodes: List[FigureNode] = []
        edges: List[FigureEdge] = []
        
        # Simple heuristic: look for common architectural keywords
        keywords = {
            "encoder": "Transformer Encoder",
            "decoder": "Transformer Decoder",
            "attention": "Self-Attention",
            "mlp": "Multi-Layer Perceptron",
            "feed-forward": "Feed Forward Network",
            "conv": "Convolutional Layer",
            "linear": "Linear Layer",
            "embedding": "Embedding Layer",
            "softmax": "Softmax",
            "layernorm": "Layer Normalization"
        }
        
        found_components = []
        for kw, label in keywords.items():
            if kw in text_lower:
                found_components.append((kw, label))
                
        # Create nodes and sequential edges based on found components
        if not found_components:
             # Default generic architecture if nothing found
             nodes = [
                 FigureNode(node_id="input", label="Input Projection", node_type="operator"),
                 FigureNode(node_id="hidden", label="Hidden Layer", node_type="operator"),
                 FigureNode(node_id="output", label="Output Projection", node_type="operator")
             ]
             edges = [
                 FigureEdge(source_id="input", target_id="hidden", tensor_flow_desc="x -> h"),
                 FigureEdge(source_id="hidden", target_id="output", tensor_flow_desc="h -> y")
             ]
             stub = (
                 "import torch.nn as nn\n\n"
                 "class Architecture(nn.Module):\n"
                 "    def __init__(self):\n"
                 "        super().__init__()\n"
                 "        self.input_proj = nn.Linear(512, 1024)\n"
                 "        self.hidden = nn.Linear(1024, 1024)\n"
                 "        self.output_proj = nn.Linear(1024, 256)\n\n"
                 "    def forward(self, x):\n"
                 "        x = self.input_proj(x)\n"
                 "        x = self.hidden(x)\n"
                 "        return self.output_proj(x)\n"
             )
        else:
             for i, (kw, label) in enumerate(found_components):
                 node_id = f"node_{i}_{kw}"
                 nodes.append(FigureNode(node_id=node_id, label=label, node_type="operator"))
                 if i > 0:
                     prev_node_id = f"node_{i-1}_{found_components[i-1][0]}"
                     edges.append(FigureEdge(
                         source_id=prev_node_id,
                         target_id=node_id,
                         tensor_flow_desc="sequential data flow"
                     ))
                     
             # Generate code stub dynamically based on found components
             stub_lines = ["import torch.nn as nn", "", "class ExtractedArchitecture(nn.Module):", "    def __init__(self):", "        super().__init__()"]
             forward_lines = ["    def forward(self, x):"]
             
             for i, (kw, _) in enumerate(found_components):
                 layer_name = f"layer_{i}_{kw}"
                 if "conv" in kw:
                     stub_lines.append(f"        self.{layer_name} = nn.Conv2d(64, 64, 3)")
                 elif "linear" in kw or "mlp" in kw or "feed-forward" in kw:
                     stub_lines.append(f"        self.{layer_name} = nn.Linear(512, 512)")
                 elif "attention" in kw:
                     stub_lines.append(f"        self.{layer_name} = nn.MultiheadAttention(512, 8)")
                 elif "embedding" in kw:
                     stub_lines.append(f"        self.{layer_name} = nn.Embedding(10000, 512)")
                 elif "layernorm" in kw:
                     stub_lines.append(f"        self.{layer_name} = nn.LayerNorm(512)")
                 else:
                     stub_lines.append(f"        self.{layer_name} = nn.Identity()  # {kw}")
                     
                 if "attention" in kw:
                     forward_lines.append(f"        x, _ = self.{layer_name}(x, x, x)")
                 else:
                     forward_lines.append(f"        x = self.{layer_name}(x)")
                     
             forward_lines.append("        return x")
             
             stub = "\n".join(stub_lines + [""] + forward_lines) + "\n"

        return FigureSemanticGraph(
            figure_id="fallback-extracted",
            caption=caption,
            nodes=nodes,
            edges=edges,
            synthesized_code_stub=stub
        )
