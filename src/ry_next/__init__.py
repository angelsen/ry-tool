"""
ry-next: Next generation command augmentation framework.

Clean architecture with semantic command understanding.
"""

__version__ = "2.0.0-alpha"

from .parser import CommandParser, ParsedCommand
from .executor import Executor, ExecutionResult
from .context import ExecutionContext
from .template import TemplateProcessor
from .loader import LibraryLoader, LibraryConfig
from .matcher import CommandMatcher, MatchResult

__all__ = [
    'CommandParser',
    'ParsedCommand',
    'Executor',
    'ExecutionResult',
    'ExecutionContext',
    'TemplateProcessor',
    'LibraryLoader',
    'LibraryConfig',
    'CommandMatcher',
    'MatchResult',
]