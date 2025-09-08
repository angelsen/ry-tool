"""
Shell executor - generates shell execution commands.
Single responsibility: convert shell script to shell command.
"""

from typing import Dict, Any
from .base import Executor
from ..config import config


class ShellExecutor(Executor):
    """Execute shell commands."""

    name = "shell"
    aliases = ("sh", "bash", "zsh")

    def compile(self, script: str, cfg: Dict[str, Any] | None = None) -> str:
        """Convert shell script to shell command."""
        cfg = cfg or {}

        # Check if base64 encoding should be used (default: true for safety)
        use_base64 = cfg.get("base64", True)
        
        if use_base64:
            shell = cfg.get("shell", config.SHELL)
            # Use base64 encoding to eliminate quoting issues
            return self.encode_script(script, shell)
        else:
            # Direct execution without encoding (needed for variable expansion)
            return script
