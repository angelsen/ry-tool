"""
Library installer and manager.

Purpose: Install libraries from various sources to user directory.
Handles copying library files and dependencies.
"""
import os
import shutil
import json
from pathlib import Path
from typing import Dict
from .loader import LibraryLoader, LibraryConfig


class LibraryInstaller:
    """Handles library installation to user directory."""
    
    def __init__(self):
        """Initialize installer with user install directory."""
        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")
        self.install_dir = Path(xdg_data) / "ry" / "libraries"
        self.install_dir.mkdir(parents=True, exist_ok=True)
        
        # Track installed libraries
        self.installed_file = self.install_dir.parent / "installed.json"
        self.installed = self._load_installed()
    
    def _load_installed(self) -> Dict:
        """Load installed libraries tracking."""
        if self.installed_file.exists():
            with open(self.installed_file) as f:
                return json.load(f)
        return {}
    
    def _save_installed(self):
        """Save installed libraries tracking."""
        with open(self.installed_file, 'w') as f:
            json.dump(self.installed, f, indent=2)
    
    def install_local(self, library: LibraryConfig) -> bool:
        """
        Install from local file to user directory.
        
        Args:
            library: LibraryConfig from a local source
        
        Returns:
            True if successful
        """
        target_dir = self.install_dir / library.name
        target_dir.mkdir(exist_ok=True)
        
        try:
            # Copy library file
            target_yaml = target_dir / f"{library.name}.yaml"
            shutil.copy2(library.path, target_yaml)
            
            # If library is in directory format, copy additional files
            if library.path.parent.name == library.name:
                source_dir = library.path.parent
                
                # Copy lib/ directory if exists
                lib_dir = source_dir / 'lib'
                if lib_dir.exists():
                    target_lib = target_dir / 'lib'
                    if target_lib.exists():
                        shutil.rmtree(target_lib)
                    shutil.copytree(lib_dir, target_lib)
                
                # Copy meta.yaml if exists
                meta_file = source_dir / 'meta.yaml'
                if meta_file.exists():
                    shutil.copy2(meta_file, target_dir / 'meta.yaml')
                
                # Copy README.md if exists
                readme = source_dir / 'README.md'
                if readme.exists():
                    shutil.copy2(readme, target_dir / 'README.md')
            
            # Update installed tracking
            self.installed[library.name] = {
                'version': library.metadata.get('version', '0.0.0'),
                'source': str(library.path),
                'type': library.type
            }
            self._save_installed()
            
            return True
            
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
    
    def install_from_registry(self, library_name: str, version: str = None) -> bool:
        """
        Install from online registry.
        
        Args:
            library_name: Name of library to install
            version: Optional version constraint
        
        Returns:
            True if successful
        """
        # For now, try to find in local development directories
        loader = LibraryLoader()
        
        try:
            # Try to load from existing sources
            library = loader.load(library_name)
            
            # Install to user directory
            return self.install_local(library)
            
        except FileNotFoundError:
            # Future: Download from online registry
            print(f"Library '{library_name}' not found in local sources")
            print("Online registry support coming soon!")
            return False
    
    def uninstall(self, library_name: str) -> bool:
        """
        Uninstall a library.
        
        Args:
            library_name: Name of library to remove
        
        Returns:
            True if successful
        """
        library_dir = self.install_dir / library_name
        
        if not library_dir.exists():
            print(f"Library '{library_name}' is not installed")
            return False
        
        try:
            shutil.rmtree(library_dir)
            
            # Update tracking
            if library_name in self.installed:
                del self.installed[library_name]
                self._save_installed()
            
            print(f"Uninstalled {library_name}")
            return True
            
        except Exception as e:
            print(f"Failed to uninstall: {e}")
            return False
    
    def list_installed(self) -> Dict[str, Dict]:
        """
        List installed libraries.
        
        Returns:
            Dictionary of installed libraries with metadata
        """
        return self.installed
    
    def update(self, library_name: str) -> bool:
        """
        Update an installed library.
        
        Args:
            library_name: Name of library to update
        
        Returns:
            True if successful
        """
        if library_name not in self.installed:
            print(f"Library '{library_name}' is not installed")
            return False
        
        # Re-install from source
        return self.install_from_registry(library_name)