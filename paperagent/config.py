"""
PaperAgent Global Configuration
Handles environment variables, API keys, paths, and runtime settings.
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings and API credentials."""
    # API Keys
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    mineru_api_key: str = Field(default_factory=lambda: os.getenv("MINERU_API_KEY", ""))
    
    # Model configuration
    default_model: str = Field(default="gemini-3.1-pro", description="Default LLM model identifier")
    temperature: float = Field(default=0.2, description="Generation temperature")
    max_tokens: int = Field(default=8192, description="Max response tokens")
    
    # Paths
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".paperagent" / "data")
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".paperagent" / "cache")
    output_dir: Path = Field(default_factory=lambda: Path.home() / ".paperagent" / "outputs")
    
    # Execution Sandbox
    sandbox_timeout_seconds: int = Field(default=30, description="Max runtime for synthesized code")
    
    # Web Server
    web_host: str = Field(default="127.0.0.1")
    web_port: int = Field(default=8000)

    def init_directories(self) -> None:
        """Ensure runtime directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# Global settings singleton
settings = Settings()
settings.init_directories()
