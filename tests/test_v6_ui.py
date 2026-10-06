import os

def test_v6_ui_html_structure() -> None:
    html_path: str = os.path.join("paperagent", "web", "static", "index.html")
    assert os.path.exists(html_path)
    with open(html_path, "r", encoding="utf-8") as f:
        content: str = f.read()

    # Verify tab buttons exist
    assert "tab-hypotheses" in content
    assert "tab-debugger" in content
    assert "tab-poster" in content

    # Verify tab-content containers exist
    assert 'id="tab-hypotheses"' in content
    assert 'id="tab-debugger"' in content
    assert 'id="tab-poster"' in content

def test_v6_ui_js_functions() -> None:
    js_path: str = os.path.join("paperagent", "web", "static", "app.js")
    assert os.path.exists(js_path)
    with open(js_path, "r", encoding="utf-8") as f:
        content: str = f.read()

    # Verify render functions exist
    assert "function renderHypotheses" in content
    assert "function renderSelfHealing" in content
    assert "function renderPoster" in content
