import re
from typing import Optional

from paperagent.models import SelfHealingResult, SelfHealingPatch
from paperagent.runner.sandbox import ExecutionSandbox
from paperagent.engine.llm_client import LLMClient


class SelfHealingDebugger:
    """
    Autonomous Execution-Feedback Self-Healing Loop.
    Executes code in a sandbox and diagnoses/fixes common runtime errors iteratively.
    """
    def heal_code(self, code: str, max_iterations: int = 3, client: Optional[LLMClient] = None) -> SelfHealingResult:
        sandbox = ExecutionSandbox()
        patches = []
        
        current_code = code
        result = None
        
        for iteration in range(1, max_iterations + 1):
            result = sandbox.run_code(current_code)
            
            if result.success:
                return SelfHealingResult(
                    success=True,
                    iterations_run=iteration,
                    patches=patches,
                    final_code=current_code,
                    final_stdout=result.stdout,
                    final_stderr=result.stderr
                )
            
            # Diagnose and patch
            error_message = result.stderr
            patched_code = current_code
            applied = False
            
            error_type = "RuntimeError"
            diagnosis = "Unknown error"
            patch_applied = ""
            
            # Check for common missing imports
            if "NameError: name 'np' is not defined" in error_message:
                error_type = "NameError"
                diagnosis = "Missing numpy import"
                patch_applied = "import numpy as np"
                patched_code = "import numpy as np\n" + current_code
                applied = True
            elif "NameError: name 'math' is not defined" in error_message:
                error_type = "NameError"
                diagnosis = "Missing math import"
                patch_applied = "import math"
                patched_code = "import math\n" + current_code
                applied = True
            elif "NameError: name 'pd' is not defined" in error_message:
                error_type = "NameError"
                diagnosis = "Missing pandas import"
                patch_applied = "import pandas as pd"
                patched_code = "import pandas as pd\n" + current_code
                applied = True
            elif "NameError: name 'plt' is not defined" in error_message:
                error_type = "NameError"
                diagnosis = "Missing matplotlib import"
                patch_applied = "import matplotlib.pyplot as plt"
                patched_code = "import matplotlib.pyplot as plt\n" + current_code
                applied = True
            
            if applied:
                patches.append(SelfHealingPatch(
                    iteration=iteration,
                    error_type=error_type,
                    error_message=error_message.strip(),
                    diagnosis=diagnosis,
                    patch_applied=patch_applied
                ))
                current_code = patched_code
            else:
                # If no heuristic matched and we can't heal it, just break early
                break

        return SelfHealingResult(
            success=False,
            iterations_run=max_iterations,
            patches=patches,
            final_code=current_code,
            final_stdout=result.stdout if result else "",
            final_stderr=result.stderr if result else ""
        )