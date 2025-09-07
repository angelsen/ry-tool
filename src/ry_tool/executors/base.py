"""
Base executor - simple interface for command generation.
Single responsibility: convert script to shell command.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class Executor(ABC):
    """Base class for all language executors."""
    
    # Subclasses should override these as class attributes
    name: str
    aliases: tuple[str, ...] = ()
    
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