import os
import tempfile
import pytest

from paperagent.models import ParsedPaper, PaperMetadata
from paperagent.synthesizer.visualizer import VisualizerSynthesizer

@pytest.fixture
def dummy_paper():
    metadata = PaperMetadata(title="Test Paper", abstract="Test abstract")
    return ParsedPaper(metadata=metadata, sections=[], source_type="test")

def test_generate_mermaid_architecture(dummy_paper):
    synthesizer = VisualizerSynthesizer()
    diagram = synthesizer.generate_mermaid_architecture(dummy_paper)

    assert diagram.diagram_type == "mermaid"
    assert "Test Paper - Architecture" in diagram.title
    assert diagram.source_code.startswith("graph ") or diagram.source_code.startswith("flowchart ")

def test_generate_matplotlib_benchmark(dummy_paper):
    synthesizer = VisualizerSynthesizer()
    diagram = synthesizer.generate_matplotlib_benchmark(dummy_paper)

    assert diagram.diagram_type == "matplotlib"
    assert "Test Paper - Benchmark Plot" in diagram.title
    assert "import matplotlib" in diagram.source_code

def test_render_matplotlib_script():
    synthesizer = VisualizerSynthesizer()

    valid_script = """import matplotlib.pyplot as plt
import numpy as np
x = np.linspace(0, 10, 100)
y = np.sin(x)
plt.plot(x, y)
"""

    invalid_script = """import matplotlib.pyplot as plt
this_is_not_valid_python_syntax!!!
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        valid_output_path = os.path.join(tmpdir, "valid.png")
        result = synthesizer.render_matplotlib_script(valid_script, valid_output_path)
        assert result is True
        assert os.path.exists(valid_output_path)

        invalid_output_path = os.path.join(tmpdir, "invalid.png")
        result = synthesizer.render_matplotlib_script(invalid_script, invalid_output_path)
        assert result is False
        assert not os.path.exists(invalid_output_path)
