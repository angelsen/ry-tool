"""
Library resolution logic for ry.
Finds and resolves library names to their YAML files.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List


class LibraryResolver:
    """Resolves library names to their YAML file paths."""
    
    def __init__(self):
        """Initialize the resolver with XDG paths."""
        # Use XDG_DATA_HOME or fallback to ~/.local/share
        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")
        self.user_libraries = Path(xdg_data) / "ry" / "libraries"
        
        # System-wide libraries (future)
        self.system_libraries = Path("/usr/share/ry/libraries")
    
    def detect_library_dir(self, config_path: Path) -> Optional[Path]:
        """
        Detect if a YAML file is part of a library and return its directory.
        
        Libraries can be in:
        - ./libraries/name/name.yaml
        - ~/.local/share/ry/libraries/name/name.yaml
        - /usr/share/ry/libraries/name/name.yaml
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Path to library directory or None if not a library
        """
        # Check if path contains '/libraries/' and ends with expected pattern
        path_parts = config_path.parts
        
        # Look for 'libraries' in the path
        if 'libraries' in path_parts:
            libs_index = path_parts.index('libraries')
            # Check if next part exists (library name)
            if libs_index + 1 < len(path_parts):
                # Library dir is up to and including the library name
                library_dir = Path(*path_parts[:libs_index + 2])
                return library_dir
        
        return None
    
    def resolve(self, name: str, args: List[str]) -> Optional[Tuple[Path, List[str]]]:
        """
        Resolve a library name or path to its YAML file.
        
        Args:
            name: Library name or path to YAML file
            args: Additional arguments passed to the library
            
        Returns:
            Tuple of (yaml_path, remaining_args) or None if not found
        """
        # If it's already a .yaml file path, use it directly
        if name.endswith(".yaml"):
            path = Path(name)
            if path.exists():
                return (path, args)
            return None
        
        # Try to resolve as a library name
        # Resolution order:
        # 1. Current directory (./name.yaml)
        # 2. User installed (~/.local/share/ry/libraries/name/name.yaml)
        # 3. System-wide (/usr/share/ry/libraries/name/name.yaml)
        
        # Check current directory
        local_file = Path(f"{name}.yaml")
        if local_file.exists():
            return (local_file, args)
        
        # Check user libraries
        if self.user_libraries.exists():
            user_lib = self.user_libraries / name / f"{name}.yaml"
            if user_lib.exists():
                return (user_lib, args)
        
        # Check system libraries (future)
        if self.system_libraries.exists():
            system_lib = self.system_libraries / name / f"{name}.yaml"
            if system_lib.exists():
                return (system_lib, args)
        
        return None
    
    def list_available(self) -> List[str]:
        """
        List all available libraries.
        
        Returns:
            List of library names
        """
        libraries = []
        
        # Add user libraries
        if self.user_libraries.exists():
            for lib_dir in self.user_libraries.iterdir():
                if lib_dir.is_dir():
                    yaml_file = lib_dir / f"{lib_dir.name}.yaml"
                    if yaml_file.exists():
                        libraries.append(lib_dir.name)
        
        # Add system libraries
        if self.system_libraries.exists():
            for lib_dir in self.system_libraries.iterdir():
                if lib_dir.is_dir():
                    yaml_file = lib_dir / f"{lib_dir.name}.yaml"
                    if yaml_file.exists() and lib_dir.name not in libraries:
                        libraries.append(lib_dir.name)
        
        return sorted(libraries)