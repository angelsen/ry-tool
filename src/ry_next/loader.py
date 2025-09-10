"""
Library loader and validator.

Purpose: Load YAML library files and validate their schema.
Understands v2 library format but doesn't execute anything.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class LibraryConfig:
    """Validated library configuration."""
    name: str
    version: str = "2.0"
    type: str = "augmentation"  # augmentation, utility, hybrid
    target: Optional[str] = None  # For augmentation libraries
    description: str = ""
    commands: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    path: Optional[Path] = None


class LibraryLoader:
    """
    Load libraries from multiple sources with priority ordering.
    
    Search order (first match wins):
    1. Direct file path (*.yaml)
    2. Local workspace (./docs_next/libraries/, ./libraries/)
    3. User libraries (~/.local/share/ry-next/libraries/)
    4. System libraries (/usr/local/share/ry-next/libraries/)
    5. Online registry (future)
    """
    
    def __init__(self, library_paths: List[Path] = None):
        """
        Initialize with search paths for libraries.
        
        Args:
            library_paths: List of directories to search for libraries
        """
        self.registry_url = os.environ.get('RY_REGISTRY_URL', None)
        self._cache_dir = Path.home() / '.cache' / 'ry-next' / 'libraries'
        self.library_paths = library_paths or self._default_paths()
    
    def _default_paths(self) -> List[Path]:
        """Get default library search paths in priority order."""
        paths = []
        
        # 1. Local development (highest priority)
        paths.append(Path.cwd() / "docs_next" / "libraries")
        paths.append(Path.cwd() / "libraries")
        
        # 2. User libraries
        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")
        paths.append(Path(xdg_data) / "ry-next" / "libraries")
        
        # 3. User config
        xdg_config = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        paths.append(Path(xdg_config) / "ry-next" / "libraries")
        
        # 4. System libraries
        paths.append(Path("/usr/local/share/ry-next/libraries"))
        
        # 5. Cached online libraries
        paths.append(self._cache_dir)
        
        return [p for p in paths if p.exists()]
    
    def load(self, library_name: str) -> LibraryConfig:
        """
        Load a library by name.
        
        Args:
            library_name: Name of the library to load
        
        Returns:
            Validated LibraryConfig
        
        Raises:
            FileNotFoundError: Library not found
            ValueError: Invalid library format
        """
        # Find library file
        library_path = self._find_library(library_name)
        if not library_path:
            raise FileNotFoundError(f"Library not found: {library_name}")
        
        # Load YAML
        try:
            with open(library_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML syntax error in {library_path}:\n{e}\n\nHint: Use block style (|) for shell commands with templates")
        
        # Validate and create config
        return self._validate_library(data, library_path)
    
    def load_file(self, path: Path) -> LibraryConfig:
        """Load a library from a specific file."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML syntax error in {path}:\n{e}\n\nHint: Use block style (|) for shell commands with templates")
        
        return self._validate_library(data, path)
    
    def _find_library(self, name: str) -> Optional[Path]:
        """
        Find library file in search paths.
        
        Looks for:
        - name/name.yaml (directory format)
        - name.yaml (single file format)
        """
        for base_path in self.library_paths:
            # Check directory format
            dir_path = base_path / name / f"{name}.yaml"
            if dir_path.exists():
                return dir_path
            
            # Check single file format
            file_path = base_path / f"{name}.yaml"
            if file_path.exists():
                return file_path
        
        return None
    
    def _validate_library(self, data: Dict[str, Any], path: Path) -> LibraryConfig:
        """
        Validate library data and create LibraryConfig.
        
        Args:
            data: Raw YAML data
            path: Path to library file
        
        Returns:
            Validated LibraryConfig
        
        Raises:
            ValueError: Invalid library format
        """
        # Check version
        version = data.get('version', '2.0')
        if not version.startswith('2'):
            raise ValueError(f"Unsupported library version: {version}")
        
        # Required fields
        if 'name' not in data:
            raise ValueError("Library missing required field: name")
        
        # Extract metadata
        metadata = {}
        if path.parent.name == data['name']:
            # Directory format - check for meta.yaml
            meta_path = path.parent / 'meta.yaml'
            if meta_path.exists():
                with open(meta_path) as f:
                    metadata = yaml.safe_load(f)
        
        # Validate commands
        commands = data.get('commands', {})
        for cmd_name, cmd_config in commands.items():
            self._validate_command(cmd_name, cmd_config)
        
        return LibraryConfig(
            name=data['name'],
            version=version,
            type=data.get('type', 'augmentation'),
            target=data.get('target'),
            description=data.get('description', ''),
            commands=commands,
            metadata=metadata,
            path=path
        )
    
    def _validate_command(self, name: str, config: Dict[str, Any]):
        """
        Validate a single command configuration.
        
        Args:
            name: Command name
            config: Command configuration
        
        Raises:
            ValueError: Invalid command format
        """
        # Check for execution mode
        has_mode = any(key in config for key in [
            'execute', 'augment', 'handlers', 'relay'
        ])
        
        if not has_mode:
            raise ValueError(f"Command '{name}' has no execution mode")
        
        # Validate flags if present
        if 'flags' in config:
            self._validate_flags(config['flags'])
        
        # Validate arguments if present
        if 'arguments' in config:
            self._validate_arguments(config['arguments'])
        
        # Validate handlers if present
        if 'handlers' in config:
            for handler in config['handlers']:
                if 'when' not in handler and 'default' not in handler:
                    raise ValueError(f"Handler in '{name}' missing 'when' or 'default'")
    
    def _validate_flags(self, flags: Dict[str, Any]):
        """Validate flag definitions."""
        for flag_name, flag_config in flags.items():
            if isinstance(flag_config, str):
                # Simple type: string, bool, int
                if flag_config not in ['string', 'bool', 'int', 'enum']:
                    raise ValueError(f"Unknown flag type: {flag_config}")
            elif isinstance(flag_config, dict):
                # Complex definition
                if 'type' in flag_config:
                    if flag_config['type'] == 'enum' and 'values' not in flag_config:
                        raise ValueError(f"Enum flag missing values: {flag_name}")
    
    def _validate_arguments(self, arguments: Dict[str, Any]):
        """Validate argument definitions."""
        for arg_name, arg_config in arguments.items():
            if isinstance(arg_config, str):
                # Simple: required, optional
                if arg_config not in ['required', 'optional']:
                    raise ValueError(f"Unknown argument type: {arg_config}")
            elif isinstance(arg_config, dict):
                # Complex definition
                if 'required' not in arg_config:
                    arg_config['required'] = False
    
    def list_available(self) -> List[str]:
        """List all available libraries."""
        libraries = set()
        
        for base_path in self.library_paths:
            if not base_path.exists():
                continue
            
            # Check for directory format libraries
            for item in base_path.iterdir():
                if item.is_dir():
                    yaml_file = item / f"{item.name}.yaml"
                    if yaml_file.exists():
                        libraries.add(item.name)
                elif item.suffix == '.yaml':
                    libraries.add(item.stem)
        
        return sorted(libraries)
    
    def list_from_path(self, path: Path) -> List[str]:
        """List libraries from a specific path."""
        libraries = []
        
        if not path.exists():
            return libraries
        
        # Check for directory format libraries
        for item in path.iterdir():
            if item.is_dir():
                yaml_file = item / f"{item.name}.yaml"
                if yaml_file.exists():
                    libraries.append(item.name)
            elif item.suffix == '.yaml':
                libraries.append(item.stem)
        
        return sorted(libraries)


