"""
Python executor - generates Python execution commands.
Single responsibility: convert Python script to shell command.
"""

from typing import Dict, Any
from .base import Executor
from ..config import config


class PythonExecutor(Executor):
    """Execute Python code."""

    name = "python"
    aliases = ("py", "python3")

    def compile(self, script: str, cfg: Dict[str, Any] | None = None) -> str:
        """Convert Python script to shell command."""
        cfg = cfg or {}

        # Add imports if specified
        if "imports" in cfg:
            imports = cfg["imports"]
            import_lines = [f"import {imp}" for imp in imports]
            script = "\n".join(import_lines) + "\n\n" + script

        interpreter = cfg.get("interpreter", config.PYTHON)

        # Use shared base64 encoding method
        return self.encode_script(script, interpreter)
