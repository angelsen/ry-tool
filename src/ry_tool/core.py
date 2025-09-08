"""
ry - A pure YAML command orchestrator.
Core execution engine for YAML configurations.
"""

from pathlib import Path
from typing import List

from .loader import RyLoader
from .template import TemplateProcessor
from .generator import CommandGenerator
from .packages import LibraryResolver
from .context import ExecutionContext


class RY:
    """YAML-based command generator with templating."""

    def __init__(self, config_path: Path, args: List[str]):
        """
        Initialize ry with a configuration path and arguments.

        Args:
            config_path: Path to YAML configuration file
            args: Arguments to pass to the configuration
        """
        # Detect library directory if applicable
        resolver = LibraryResolver()
        library_dir = resolver.detect_library_dir(config_path)

        # Create execution context
        self.context = ExecutionContext(
            config_path=config_path, args=args, library_dir=library_dir
        )

        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load YAML configuration with custom loader."""
        # Create loader and set context
        with open(self.context.config_path) as f:
            # Create loader instance
            loader = RyLoader(f)
            loader.args = self.context.args
            loader.name = str(self.context.config_path)

            # Load YAML with custom tags
            try:
                config = loader.get_single_data()
            finally:
                loader.dispose()

        return config or {}

    def run(self) -> int:
        """
        Generate and output commands.

        Returns:
            Exit code (0 for success)
        """
        # Create template processor
        processor = TemplateProcessor(self.context.args)

        # Create generator with context
        generator = CommandGenerator(self.config, self.context, processor)

        # Generate commands
        output = generator.generate()

        # Output to stdout
        if output:
            print(output)

        return 0
