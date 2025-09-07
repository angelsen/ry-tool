"""
Pipeline context - simple state holder for pipeline execution.
Single responsibility: hold pipeline state, nothing more.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class PipeMode(Enum):
    """How commands should be connected."""
    SEQUENCE = "sequence"  # Run one after another (default)
    PIPELINE = "pipeline"  # Connect with pipes
    PARALLEL = "parallel"  # Run simultaneously


@dataclass
class PipelineContext:
    """Simple state holder for pipeline execution."""
    steps: List[Dict[str, Any]]
    mode: PipeMode = PipeMode.SEQUENCE
    fail_fast: bool = True
    
    @property
    def count(self) -> int:
        """Number of steps."""
        return len(self.steps)