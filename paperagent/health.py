import os
import sys
import subprocess
from typing import Dict, Any

from paperagent.config import settings

def check_system_health() -> Dict[str, Any]:
    """
    Check the health and configuration status of the PaperAgent system.
    """
    status = "healthy"

    # Check sandbox availability
    try:
        result = subprocess.run(
            [sys.executable, "-c", "print('ok')"],
            capture_output=True,
            text=True,
            timeout=5
        )
        sandbox_available = result.returncode == 0 and result.stdout.strip() == "ok"
    except Exception:
        sandbox_available = False
        status = "degraded"

    # Check storage directory writability
    storage_dir_writable = False
    if settings.data_dir.exists():
        storage_dir_writable = os.access(settings.data_dir, os.W_OK)
    if not storage_dir_writable:
        status = "degraded"

    # Check configured providers
    configured_providers = []
    if settings.gemini_api_key:
        configured_providers.append("Gemini")
    if settings.openai_api_key:
        configured_providers.append("OpenAI")

    if not configured_providers:
        configured_providers.append("Mock fallback")
        status = "degraded"

    return {
        "status": status,
        "version": "0.2.0",
        "python_version": sys.version,
        "sandbox_available": sandbox_available,
        "storage_dir_writable": storage_dir_writable,
        "configured_providers": configured_providers
    }
