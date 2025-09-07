"""
Python executor - generates Python execution commands.
Single responsibility: convert Python script to shell command.
"""

import shlex
from typing import Dict, Any
from .base import Executor


class PythonExecutor(Executor):
    """Execute Python code."""

    name = "python"
    aliases = ("py", "python3")

    def compile(self, script: str, config: Dict[str, Any] | None = None) -> str:
        """Convert Python script to shell command."""
        config = config or {}

        # Add imports if specified
        if "imports" in config:
            imports = config["imports"]
            import_lines = [f"import {imp}" for imp in imports]
            script = "\n".join(import_lines) + "\n\n" + script

        # Choose interpreter
        interpreter = config.get("interpreter", "python3")

        # Use -c with proper escaping (works with pipes!)
        return f"{interpreter} -c {shlex.quote(script)}"
