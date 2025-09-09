#!/usr/bin/env python3
"""
Self-contained registry updater for ry-lib.
Scans docs/libraries and updates registry.json.
"""
import json
import os
import sys
import yaml
from pathlib import Path

REGISTRY_VERSION = "1.0.0"
BASE_URL = "https://angelsen.github.io/ry-tool/libraries"

def scan_libraries(libraries_dir):
    """Scan libraries directory and extract metadata."""
    libraries = {}
    
    if not libraries_dir.exists():
        print(f"ERROR: Libraries directory not found: {libraries_dir}", file=sys.stderr)
        return libraries
    
    for lib_dir in sorted(libraries_dir.iterdir()):
        if not lib_dir.is_dir():
            continue
        
        # Skip hidden directories and common non-library directories
        if lib_dir.name.startswith('.') or lib_dir.name in ['STYLE_GUIDE.md']:
            continue
        
        # Check for main YAML file
        yaml_file = lib_dir / f"{lib_dir.name}.yaml"
        if not yaml_file.exists():
            print(f"  ⚠️  {lib_dir.name}: Missing {lib_dir.name}.yaml", file=sys.stderr)
            continue
        
        # Collect all files
        files = []
        for item in lib_dir.rglob("*"):
            if item.is_file():
                # Get relative path from library directory
                rel_path = item.relative_to(lib_dir)
                file_str = str(rel_path)
                
                # Skip cache and temporary files
                if any(part.startswith('.') for part in rel_path.parts):
                    continue
                if file_str.endswith(('.pyc', '.pyo', '.pyd', '__pycache__')):
                    continue
                
                # Only include relevant file types
                extensions = ('.py', '.yaml', '.yml', '.md', '.txt', '.json', '.sh', '.bash')
                if item.suffix in extensions or item.name in ['README', 'LICENSE', 'CHANGELOG']:
                    files.append(file_str)
        
        # Load metadata from meta.yaml
        meta = {}
        meta_file = lib_dir / "meta.yaml"
        if meta_file.exists():
            try:
                with open(meta_file) as f:
                    meta = yaml.safe_load(f) or {}
            except (yaml.YAMLError, OSError) as e:
                print(f"  ⚠️  {lib_dir.name}: Error reading meta.yaml: {e}", file=sys.stderr)
        
        # Build library entry
        library = {
            "files": sorted(files),
            "entry": f"{lib_dir.name}.yaml"
        }
        
        # Add optional fields from meta.yaml
        for field in ["description", "version", "author", "dependencies"]:
            if field in meta:
                library[field] = meta[field]
        
        libraries[lib_dir.name] = library
    
    return libraries

def update_registry():
    """Update the registry.json file."""
    # Find project root (where docs/ is)
    current = Path.cwd()
    docs_dir = current / "docs"
    
    # If we're running from within the project, find the root
    if not docs_dir.exists():
        # Try parent directories
        for parent in current.parents:
            if (parent / "docs" / "libraries").exists():
                docs_dir = parent / "docs"
                break
    
    if not docs_dir.exists():
        print("ERROR: Cannot find docs directory", file=sys.stderr)
        print("  Run this from the ry-tool project root", file=sys.stderr)
        sys.exit(1)
    
    libraries_dir = docs_dir / "libraries"
    registry_file = docs_dir / "registry.json"
    
    print("📋 Updating registry...")
    
    # Scan libraries
    libraries = scan_libraries(libraries_dir)
    
    # Build registry
    registry = {
        "version": REGISTRY_VERSION,
        "base_url": BASE_URL,
        "libraries": libraries
    }
    
    # Save registry
    with open(registry_file, "w") as f:
        json.dump(registry, f, indent=2)
    
    lib_count = len(libraries)
    print(f"SUCCESS: Registry updated with {lib_count} libraries", file=sys.stderr)
    print(f"   File: {registry_file}", file=sys.stderr)
    
    return 0

if __name__ == "__main__":
    sys.exit(update_registry())