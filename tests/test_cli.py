import pytest
import subprocess
from unittest.mock import patch
import sys

from paperagent.cli import main

def test_cli_parse(capsys):
    test_args = ["paperagent", "parse", "1234.5678"]
    with patch.object(sys, 'argv', test_args):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "Mock Title" in captured.out
    assert "Formulas Extracted" in captured.out

def test_cli_analyze(capsys):
    test_args = ["paperagent", "analyze", "1234.5678"]
    with patch.object(sys, 'argv', test_args):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "Executive Brief" in captured.out
    assert "Reviewer Critique" in captured.out

def test_cli_synthesize(capsys):
    test_args = ["paperagent", "synthesize", "1234.5678"]
    with patch.object(sys, 'argv', test_args):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "Synthesized Code" in captured.out
    assert "def mock_algorithm" in captured.out

def test_cli_run(capsys):
    test_args = ["paperagent", "run", "1234.5678"]
    with patch.object(sys, 'argv', test_args):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

    captured = capsys.readouterr()
    assert "Execution Successful" in captured.out
    assert "Tests passed!" in captured.out
