from .sandbox import ExecutionSandbox
from .streaming import StreamingSandboxRunner
from paperagent.models import ExecutionResult
from paperagent.config import settings

def execute_code(code: str, timeout: int = None) -> ExecutionResult:
    """Standalone helper function to quickly run Python code in the sandbox."""
    if timeout is None:
        timeout = settings.sandbox_timeout_seconds
    sandbox = ExecutionSandbox()
    return sandbox.run_code(code, timeout=timeout)

__all__ = ["ExecutionSandbox", "StreamingSandboxRunner", "execute_code"]
