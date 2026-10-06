import os

def test_web_ui_html_structure():
    html_path = os.path.join("paperagent", "web", "static", "index.html")
    assert os.path.exists(html_path)
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify tab buttons exist
    assert "tab-committee" in content
    assert "tab-scorecard" in content
    assert "tab-podcast" in content

    # Verify tab-content containers exist
    assert 'id="tab-committee"' in content
    assert 'id="tab-scorecard"' in content
    assert 'id="tab-podcast"' in content

    # Verify content placeholders exist
    assert 'id="committeeContent"' in content
    assert 'id="scorecardContent"' in content
    assert 'id="podcastContent"' in content

def test_web_ui_js_functions():
    js_path = os.path.join("paperagent", "web", "static", "app.js")
    assert os.path.exists(js_path)
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify render functions exist
    assert "function renderCommitteeReview" in content
    assert "function renderScorecard" in content
    assert "function renderPodcast" in content
