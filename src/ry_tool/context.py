"""
Execution context for ry.
Single responsibility: hold all execution state in one place.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class ExecutionContext:
    """Holds all state needed during YAML execution."""
    
    config_path: Path
    args: List[str]
    library_dir: Optional[Path] = None
    env: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialize environment if not provided."""
        if self.env is None:
            self.env = {}
    
    @property
    def is_library(self) -> bool:
        """Check if this is a library execution."""
        return self.library_dir is not None
    
    def get_env_exports(self) -> List[str]:
        """Get environment export commands."""
        exports = []
        
        # Add RY_LIBRARY_DIR if in library context
        if self.library_dir:
            exports.append(f"export RY_LIBRARY_DIR={self.library_dir}")
        
        # Add any additional environment variables
        for key, value in self.env.items():
            exports.append(f"export {key}={value}")
        
        return exports