import os
import re
import subprocess
import sys
import tempfile
from typing import Optional

from paperagent.models import DiagramArtifact, ParsedPaper
from paperagent.engine.llm_client import LLMClient

MERMAID_FALLBACK = """graph TD
    A[Input Data] --> B[Model Architecture]
    B --> C[Output Predictions]
"""

MATPLOTLIB_FALLBACK = """import matplotlib.pyplot as plt
import numpy as np

def generate_plot(output_path):
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    plt.plot(x, y, label="Benchmark")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Mock Benchmark Plot")
    plt.legend()
    plt.savefig(output_path)
    plt.close()

if __name__ == '__main__':
    generate_plot("benchmark.png")
"""

class VisualizerSynthesizer:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def generate_mermaid_architecture(self, paper: ParsedPaper) -> DiagramArtifact:
        title = f"{paper.metadata.title} - Architecture"

        if not getattr(self.llm_client, "gemini_api_key", None) and not getattr(self.llm_client, "openai_api_key", None):
            return DiagramArtifact(
                diagram_type="mermaid",
                title=title,
                source_code=MERMAID_FALLBACK
            )

        prompt = f"""
        Based on the paper titled "{paper.metadata.title}", generate a clean, valid Mermaid flowchart
        ('graph TD' or 'flowchart TD') representing the model architecture or pipeline (nodes, arrows, tensor shapes/steps).

        Do not wrap the response in ```mermaid ... ```. Only return the valid Mermaid script.
        """

        try:
            mermaid_str = self.llm_client.generate(prompt)
            mermaid_str = re.sub(r"^```mermaid\s*", "", mermaid_str, flags=re.IGNORECASE)
            mermaid_str = re.sub(r"^```\s*", "", mermaid_str, flags=re.IGNORECASE)
            mermaid_str = re.sub(r"\s*```$", "", mermaid_str)
            mermaid_str = mermaid_str.strip()

            if not mermaid_str.startswith("graph ") and not mermaid_str.startswith("flowchart "):
                mermaid_str = MERMAID_FALLBACK

            return DiagramArtifact(
                diagram_type="mermaid",
                title=title,
                source_code=mermaid_str
            )
        except Exception:
            return DiagramArtifact(
                diagram_type="mermaid",
                title=title,
                source_code=MERMAID_FALLBACK
            )

    def generate_matplotlib_benchmark(self, paper: ParsedPaper) -> DiagramArtifact:
        title = f"{paper.metadata.title} - Benchmark Plot"

        if not getattr(self.llm_client, "gemini_api_key", None) and not getattr(self.llm_client, "openai_api_key", None):
            return DiagramArtifact(
                diagram_type="matplotlib",
                title=title,
                source_code=MATPLOTLIB_FALLBACK
            )

        prompt = f"""
        Based on the paper titled "{paper.metadata.title}", write a runnable Python script using `matplotlib.pyplot`
        that plots a synthetic comparison benchmark (e.g., theoretical complexity vs sequence length, training loss curve, or throughput).
        The script should include `import matplotlib.pyplot as plt`. Do not call `plt.show()`, just setup the plot.

        Do not wrap the response in ```python ... ```. Only return the valid Python script.
        """

        try:
            script_str = self.llm_client.generate(prompt)
            script_str = re.sub(r"^```python\s*", "", script_str, flags=re.IGNORECASE)
            script_str = re.sub(r"^```\s*", "", script_str, flags=re.IGNORECASE)
            script_str = re.sub(r"\s*```$", "", script_str)
            script_str = script_str.strip()

            if "import matplotlib" not in script_str:
                script_str = MATPLOTLIB_FALLBACK

            return DiagramArtifact(
                diagram_type="matplotlib",
                title=title,
                source_code=script_str
            )
        except Exception:
            return DiagramArtifact(
                diagram_type="matplotlib",
                title=title,
                source_code=MATPLOTLIB_FALLBACK
            )

    def render_matplotlib_script(self, script_code: str, output_image_path: str) -> bool:
        # Prevent showing plot interactively, force savefig
        modified_script = script_code
        # Remove plt.show()
        modified_script = re.sub(r'plt\.show\(\)', '', modified_script)

        # Inject savefig if not present or just ensure it saves to correct path
        escaped_path = output_image_path.replace('\\', '\\\\')
        if 'plt.savefig' not in modified_script:
            modified_script += f'\nimport matplotlib.pyplot as plt\nplt.savefig(r"{escaped_path}")'
        else:
            # Replace any plt.savefig(...) with the exact path
            modified_script = re.sub(r'plt\.savefig\([^)]+\)', f'plt.savefig(r"{escaped_path}")', modified_script)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(modified_script)
            temp_path = temp_file.name

        try:
            # Run the python script in a subprocess
            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                print(f"Error executing matplotlib script:\n{result.stderr}")
                return False

            if os.path.exists(output_image_path):
                return True
            return False
        except Exception as e:
            print(f"Exception during matplotlib execution: {e}")
            return False
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
