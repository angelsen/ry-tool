"""
Registry management for ry libraries.
Handles reading, writing, and validating the library registry.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


# Registry format version (for future compatibility)
REGISTRY_VERSION = "1.0.0"


class Registry:
    """Manages the ry library registry."""
    
    def __init__(self, base_url: str = "https://angelsen.github.io/ry-tool"):
        """
        Initialize registry with base URL.
        
        Args:
            base_url: Base URL for the registry (GitHub Pages)
        """
        self.base_url = base_url
        self.registry_url = f"{base_url}/docs/registry.json"
        self.libraries_url = f"{base_url}/libraries"
        
        # Local paths - hybrid structure
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.docs_dir = self.project_root / "docs"
        self.libraries_dir = self.project_root / "libraries"  # Libraries at root
        self.registry_file = self.docs_dir / "registry.json"  # Registry in docs
    
    def fetch_remote(self) -> Optional[Dict]:
        """
        Fetch the remote registry.
        
        Returns:
            Registry data or None if failed
        """
        try:
            result = subprocess.run(
                ["curl", "-sL", self.registry_url],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None
    
    def load_local(self) -> Dict:
        """
        Load the local registry file.
        
        Returns:
            Registry data or empty registry structure if not found
        """
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        
        # Return minimal empty structure
        return {
            "version": REGISTRY_VERSION,  # Registry format version
            "base_url": self.libraries_url,
            "libraries": {}
        }
    
    def save_local(self, registry: Dict):
        """
        Save the registry to the local file.
        
        Args:
            registry: Registry data to save
        """
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, "w") as f:
            json.dump(registry, f, indent=2)
    
    def scan_libraries(self) -> Dict[str, Dict]:
        """
        Scan the docs/libraries directory and extract metadata.
        
        Returns:
            Dictionary of library name -> metadata
        """
        libraries = {}
        
        if not self.libraries_dir.exists():
            return libraries
        
        for lib_dir in self.libraries_dir.iterdir():
            if not lib_dir.is_dir():
                continue
            
            # Look for main YAML file
            yaml_file = lib_dir / f"{lib_dir.name}.yaml"
            if not yaml_file.exists():
                continue
            
            # Extract metadata
            metadata = self._extract_metadata(lib_dir)
            if metadata:
                libraries[lib_dir.name] = metadata
        
        return libraries
    
    def _extract_metadata(self, lib_dir: Path) -> Optional[Dict]:
        """
        Extract metadata from a library directory.
        
        Args:
            lib_dir: Path to library directory
            
        Returns:
            Library metadata or None if invalid
        """
        lib_name = lib_dir.name
        yaml_file = lib_dir / f"{lib_name}.yaml"
        
        if not yaml_file.exists():
            return None
        
        # Get all files in the library
        files = []
        for item in lib_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(lib_dir)
                files.append(str(rel_path))
        
        # Look for meta.yaml for additional info
        meta = {}
        meta_file = lib_dir / "meta.yaml"
        if meta_file.exists():
            try:
                import yaml
                with open(meta_file) as f:
                    meta = yaml.safe_load(f) or {}
            except (FileNotFoundError, yaml.YAMLError):
                pass
        
        # Build metadata - only include what we actually know
        metadata = {
            "files": sorted(files),
            "entry": f"{lib_name}.yaml"
        }
        
        # Only add fields if they exist in meta.yaml
        if "description" in meta:
            metadata["description"] = meta["description"]
        if "version" in meta:
            metadata["version"] = meta["version"]
        if "author" in meta:
            metadata["author"] = meta["author"]
        
        return metadata
    
    def update_registry(self) -> Dict:
        """
        Update the registry by scanning libraries.
        
        Returns:
            Updated registry data
        """
        registry = self.load_local()
        libraries = self.scan_libraries()
        
        registry["libraries"] = libraries
        registry["base_url"] = self.libraries_url
        registry["version"] = REGISTRY_VERSION
        
        return registry
    
    def search(self, query: str = "") -> List[Dict]:
        """
        Search the registry for libraries.
        
        Args:
            query: Search term (matches name or description)
            
        Returns:
            List of matching libraries
        """
        registry = self.fetch_remote() or self.load_local()
        results = []
        
        query_lower = query.lower()
        
        for name, info in registry.get("libraries", {}).items():
            if not query or (
                query_lower in name.lower() or
                query_lower in info.get("description", "").lower()
            ):
                results.append({
                    "name": name,
                    **info
                })
        
        return results