"""
Execution context for ry.
Single responsibility: hold all execution state in one place.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict
import yaml


@dataclass
class ExecutionContext:
    """Holds all state needed during YAML execution."""

    config_path: Path
    args: List[str]
    library_dir: Optional[Path] = None
    env: Dict[str, str] = None
    library_meta: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize environment and load library metadata if needed."""
        if self.env is None:
            self.env = {}
        
        # Load library metadata if in library context
        if self.library_dir:
            self.library_meta = self._load_library_meta()

    def _load_library_meta(self) -> Dict[str, str]:
        """Load library metadata from meta.yaml."""
        meta_path = self.library_dir / 'meta.yaml'
        if meta_path.exists():
            with open(meta_path) as f:
                meta = yaml.safe_load(f)
                return {
                    'library_name': meta.get('name', self.library_dir.name),
                    'library_version': meta.get('version', 'unknown'),
                    'library_description': meta.get('description', ''),
                    'library_author': meta.get('author', 'unknown')
                }
        return {
            'library_name': self.library_dir.name,
            'library_version': 'unknown'
        }

    @property
    def is_library(self) -> bool:
        """Check if this is a library execution."""
        return self.library_dir is not None

    def get_env_exports(self) -> List[str]:
        """Get environment export commands."""
        exports = []

        # Add RY_LIBRARY_DIR if in library context
        if self.library_dir:
            # Use absolute path for reliability
            exports.append(f"export RY_LIBRARY_DIR={self.library_dir.absolute()}")

        # Add any additional environment variables
        for key, value in self.env.items():
            exports.append(f"export {key}={value}")

        return exports
