"""
ry - A pure YAML command orchestrator.
Generates shell commands from YAML configurations with automatic templating.
"""
import os
import sys
from pathlib import Path
from typing import List

from .loader import RyLoader
from .template import TemplateProcessor
from .generator import CommandGenerator

class RY:
    """Pure YAML-based command generator with templating."""
    
    def __init__(self):
        """Initialize ry."""
        # Parse arguments
        self.config_path, self.args = self._parse_args()
        
        # Load configuration with custom YAML tags
        self.config = self._load_config()
    
    def _parse_args(self) -> tuple[Path, List[str]]:
        """Parse command line arguments."""
        # Check for config file
        if len(sys.argv) > 1 and sys.argv[1].endswith('.yaml'):
            config_path = Path(sys.argv[1])
            args = sys.argv[2:]
        elif 'RY_CONFIG' in os.environ:
            config_path = Path(os.environ['RY_CONFIG'])
            args = sys.argv[1:]
        else:
            print("FAIL: no config file specified", file=sys.stderr)
            print("  Usage: ry <config.yaml> [args...]", file=sys.stderr)
            print("  Or set: RY_CONFIG=path/to/config.yaml", file=sys.stderr)
            sys.exit(1)
        
        return config_path, args
    
    def _load_config(self) -> dict:
        """Load YAML configuration with custom loader."""
        if not self.config_path.exists():
            print(f"FAIL: config not found - {self.config_path}", file=sys.stderr)
            sys.exit(1)
        
        # Create loader and set context
        with open(self.config_path) as f:
            # Create loader instance
            loader = RyLoader(f)
            loader.args = self.args
            loader.name = str(self.config_path)
            
            # Load YAML with custom tags
            try:
                config = loader.get_single_data()
            finally:
                loader.dispose()
        
        return config or {}
    
    def run(self) -> int:
        """Generate and output commands."""
        # Create template processor
        processor = TemplateProcessor(self.args)
        
        # Create generator with config and processor
        generator = CommandGenerator(self.config, self.args, processor)
        
        # Generate commands
        output = generator.generate()
        
        # Output to stdout
        if output:
            print(output)
        
        return 0