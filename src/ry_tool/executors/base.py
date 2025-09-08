"""
Base executor - simple interface for command generation.
Single responsibility: convert script to shell command.
"""

import base64
from abc import ABC, abstractmethod
from typing import Dict, Any


class Executor(ABC):
    """Base class for all language executors."""

    # Subclasses should override these as class attributes
    name: str
    aliases: tuple[str, ...] = ()

    def encode_script(self, script: str, interpreter: str) -> str:
        """
        Universal base64 encoding pipeline for any script.
        Eliminates all shell quoting issues by encoding the script.

        Args:
            script: The code to execute
            interpreter: Path to interpreter binary

        Returns:
            Shell command that decodes and executes the script
        """
        encoded = base64.b64encode(script.encode()).decode()
        return f"echo {encoded} | base64 -d | {interpreter}"

    @abstractmethod
    def compile(self, script: str, config: Dict[str, Any] | None = None) -> str:
        """
        Convert script to shell command.

        Args:
            script: The code to execute
            config: Optional configuration

        Returns:
            Shell command string
        """
        pass
