import os
import sys
import time
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from paperagent.models import ExecutionResult
from paperagent.config import settings

class ExecutionSandbox:
    """Safely executes generated Python code in a subprocess."""

    ARTIFACT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".csv", ".json"}

    def __init__(self):
        # Ensure output directory exists
        settings.output_dir.mkdir(parents=True, exist_ok=True)

    def _scan_and_copy_artifacts(self, temp_dir: Path) -> list[str]:
        """Scans temp directory for generated files and copies them to output dir."""
        generated_artifacts = []
        for file_path in temp_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.ARTIFACT_EXTENSIONS:
                # Copy to output directory
                dest_path = settings.output_dir / file_path.name
                # If file exists, append timestamp to name to avoid overwrite
                if dest_path.exists():
                    timestamp = int(time.time() * 1000)
                    dest_path = settings.output_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"

                shutil.copy2(file_path, dest_path)
                generated_artifacts.append(str(dest_path))

        return generated_artifacts

    def run_code(self, code: str, timeout: int = None) -> ExecutionResult:
        """
        Executes Python code in an isolated temporary directory.
        Captures output, errors, execution time, and any generated artifacts.
        """
        if timeout is None:
            timeout = settings.sandbox_timeout_seconds

        start_time = time.time()

        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            target_file = temp_dir / "run_target.py"
            target_file.write_text(code, encoding="utf-8")

            try:
                result = subprocess.run(
                    [sys.executable, str(target_file)],
                    cwd=str(temp_dir),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                success = result.returncode == 0
                exit_code = result.returncode
                stdout = result.stdout
                stderr = result.stderr

            except subprocess.TimeoutExpired as e:
                success = False
                exit_code = -1
                # When text=True, e.stdout and e.stderr are already strings or None
                stdout = str(e.stdout) if e.stdout else ""
                stderr = str(e.stderr) if e.stderr else f"Execution timed out after {timeout} seconds."
            except Exception as e:
                success = False
                exit_code = -1
                stdout = ""
                stderr = f"Sandbox execution error: {str(e)}"

            execution_time = time.time() - start_time

            # Scan for generated artifacts
            artifacts = self._scan_and_copy_artifacts(temp_dir)

            return ExecutionResult(
                success=success,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time_seconds=execution_time,
                generated_artifacts=artifacts
            )

    def run_tests(self, module_code: str, test_code: str, timeout: int = None) -> ExecutionResult:
        """
        Executes a module and its corresponding PyTest / Unittest test suite.
        """
        if timeout is None:
            timeout = settings.sandbox_timeout_seconds

        start_time = time.time()

        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)

            module_file = temp_dir / "run_target.py"
            module_file.write_text(module_code, encoding="utf-8")

            test_file = temp_dir / "test_target.py"
            test_file.write_text(test_code, encoding="utf-8")

            try:
                # Assuming the tests are written using standard unittest module
                result = subprocess.run(
                    [sys.executable, "-m", "unittest", str(test_file.name)],
                    cwd=str(temp_dir),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                success = result.returncode == 0
                exit_code = result.returncode
                stdout = result.stdout
                stderr = result.stderr

            except subprocess.TimeoutExpired as e:
                success = False
                exit_code = -1
                # When text=True, e.stdout and e.stderr are already strings or None
                stdout = str(e.stdout) if e.stdout else ""
                stderr = str(e.stderr) if e.stderr else f"Execution timed out after {timeout} seconds."
            except Exception as e:
                success = False
                exit_code = -1
                stdout = ""
                stderr = f"Sandbox test execution error: {str(e)}"

            execution_time = time.time() - start_time

            # Scan for generated artifacts
            artifacts = self._scan_and_copy_artifacts(temp_dir)

            return ExecutionResult(
                success=success,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time_seconds=execution_time,
                generated_artifacts=artifacts
            )
