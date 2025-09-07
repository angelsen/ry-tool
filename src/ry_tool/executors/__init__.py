"""
Executor registry - maps names to executors.
Single responsibility: executor lookup.
"""

from typing import Dict, Optional
from .base import Executor
from .shell import ShellExecutor
from .python import PythonExecutor


class Registry:
    """Simple registry for executors."""

    def __init__(self):
        self._executors: Dict[str, Executor] = {}

        # Register built-in executors
        self.register(ShellExecutor())
        self.register(PythonExecutor())

    def register(self, executor: Executor) -> None:
        """Register an executor."""
        # Register by canonical name
        self._executors[executor.name] = executor

        # Register aliases
        for alias in executor.aliases:
            self._executors[alias] = executor

    def get(self, name: str) -> Optional[Executor]:
        """Get executor by name or alias."""
        return self._executors.get(name)

    def has(self, name: str) -> bool:
        """Check if executor exists."""
        return name in self._executors


# Global registry
registry = Registry()
