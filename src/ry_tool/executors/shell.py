"""
Shell executor - generates shell execution commands.
Single responsibility: convert shell script to shell command.
"""

import shlex
from typing import Dict, Any
from .base import Executor


class ShellExecutor(Executor):
    """Execute shell commands."""

    name = "shell"
    aliases = ("sh", "bash", "zsh")

    def compile(self, script: str, config: Dict[str, Any] | None = None) -> str:
        """Convert shell script to shell command."""
        config = config or {}

        # Determine shell
        shell = config.get("shell", "sh")

        # Single line commands can run directly
        if "\n" not in script and not any(c in script for c in ["'", '"', "$", "`"]):
            return script

        # Complex commands: use -c with proper escaping
        return f"{shell} -c {shlex.quote(script)}"
