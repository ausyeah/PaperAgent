import pytest
from pathlib import Path
from paperagent.runner import ExecutionSandbox, execute_code
from paperagent.config import settings

def test_run_code_success():
    code = "print('Hello, Sandbox!')"
    result = execute_code(code)

    assert result.success is True
    assert result.exit_code == 0
    assert "Hello, Sandbox!" in result.stdout
    assert result.stderr == ""
    assert result.execution_time_seconds > 0

def test_run_code_syntax_error():
    code = "print('Missing quote)"
    result = execute_code(code)

    assert result.success is False
    assert result.exit_code != 0
    assert "SyntaxError" in result.stderr

def test_run_code_timeout():
    # Should timeout after 1 second
    code = "import time\ntime.sleep(5)"
    result = execute_code(code, timeout=1)

    assert result.success is False
    assert result.exit_code == -1
    assert "timed out" in result.stderr or result.stderr == ""

def test_run_code_artifact_detection():
    # Create a code that writes to a .csv file
    code = '''
import csv
with open("test_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["col1", "col2"])
    writer.writerow([1, 2])
'''
    sandbox = ExecutionSandbox()
    result = sandbox.run_code(code)

    assert result.success is True
    assert result.exit_code == 0

    # We should have one artifact detected
    assert len(result.generated_artifacts) == 1
    artifact_path = Path(result.generated_artifacts[0])
    assert artifact_path.exists()
    assert artifact_path.suffix == ".csv"

    # Clean up the output file
    if artifact_path.exists():
        artifact_path.unlink()

def test_run_tests_success():
    module_code = '''
def add(a, b):
    return a + b
'''
    test_code = '''
import unittest
from run_target import add

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

if __name__ == "__main__":
    unittest.main()
'''
    sandbox = ExecutionSandbox()
    result = sandbox.run_tests(module_code, test_code)

    assert result.success is True
    assert result.exit_code == 0
    assert "Ran 1 test" in result.stderr or "Ran 1 test" in result.stdout

def test_run_code_timeout_with_output():
    # Should timeout after 1 second, but generate output first
    # Using sys.stdout.flush() to ensure output is captured before sleep
    code = "import time; import sys; print('starting'); sys.stdout.flush(); time.sleep(5)"
    result = execute_code(code, timeout=1)

    assert result.success is False
    assert result.exit_code == -1
    assert "starting" in result.stdout
    assert "timed out" in result.stderr or result.stderr == ""
