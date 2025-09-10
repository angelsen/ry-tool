#!/usr/bin/env python3
"""Validate ry library structure and content."""

import sys
import yaml
from pathlib import Path
from typing import List, Optional


def find_libraries_dir() -> Optional[Path]:
    """Find the libraries directory."""
    for path in [Path('docs/libraries'), Path('libraries')]:
        if path.exists():
            return path
    return None


def load_yaml(file_path: Path) -> Optional[dict]:
    """Load YAML file."""
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def validate_library(name: str, verbose: bool = False) -> bool:
    """
    Validate a specific library.
    
    Args:
        name: Library name to validate
        verbose: Show detailed information
    
    Returns:
        True if valid, False otherwise
    """
    lib_base = find_libraries_dir()
    if not lib_base:
        print("ERROR: No libraries directory found", file=sys.stderr)
        return False
    
    lib_dir = lib_base / name
    if not lib_dir.exists():
        print(f"ERROR: Library not found: {name}", file=sys.stderr)
        return False
    
    lib_yaml = lib_dir / f"{name}.yaml"
    if not lib_yaml.exists():
        print(f"ERROR: Missing {name}.yaml", file=sys.stderr)
        return False
    
    try:
        # Load library configuration
        data = load_yaml(lib_yaml)
        if not data:
            print(f"ERROR: Could not load {name}.yaml", file=sys.stderr)
            return False
        
        # Validate structure
        errors = []
        
        if data.get('version') != '2.0':
            errors.append("Must be version 2.0")
        if 'name' not in data:
            errors.append("Missing name field")
        if 'type' not in data:
            errors.append("Missing type field")
        elif data['type'] not in ['augmentation', 'utility', 'hybrid']:
            errors.append(f"Invalid type: {data['type']}")
        
        if data.get('type') == 'augmentation':
            # Check for target or relay commands
            has_target = 'target' in data
            has_relay = any('relay' in cmd for cmd in data.get('commands', {}).values())
            if not (has_target or has_relay):
                errors.append("Augmentation library needs target or relay commands")
        
        # Check meta.yaml
        meta_yaml = lib_dir / 'meta.yaml'
        if meta_yaml.exists():
            meta = load_yaml(meta_yaml)
            if meta:
                if 'version' not in meta:
                    errors.append("meta.yaml missing version")
                if 'name' not in meta:
                    errors.append("meta.yaml missing name")
        
        if errors:
            print(f"ERROR: {name}: Invalid", file=sys.stderr)
            for error in errors:
                print(f"   - {error}", file=sys.stderr)
            return False
        
        print(f"SUCCESS: {name}: Valid", file=sys.stderr)
        
        if verbose:
            print(f"   Version: {data.get('version')}", file=sys.stderr)
            print(f"   Type: {data.get('type')}", file=sys.stderr)
            print(f"   Commands: {len(data.get('commands', {}))}", file=sys.stderr)
            if meta_yaml.exists():
                meta = load_yaml(meta_yaml)
                if meta:
                    print(f"   Library version: {meta.get('version', '0.0.0')}", file=sys.stderr)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {name}: {e}", file=sys.stderr)
        return False


def validate_all(verbose: bool = False) -> bool:
    """
    Validate all libraries.
    
    Args:
        verbose: Show detailed information
    
    Returns:
        True if all valid, False if any failed
    """
    lib_base = find_libraries_dir()
    if not lib_base:
        print("ERROR: No libraries directory found", file=sys.stderr)
        return False
    
    # Find all library directories
    libraries = []
    for item in lib_base.iterdir():
        if item.is_dir() and (item / f"{item.name}.yaml").exists():
            libraries.append(item.name)
    
    if not libraries:
        print("INFO: No libraries found", file=sys.stderr)
        return True
    
    failed = []
    validated = 0
    
    for lib_name in sorted(libraries):
        if validate_library(lib_name, verbose):
            validated += 1
        else:
            failed.append(lib_name)
    
    print(f"SUCCESS: Validated {validated} libraries", file=sys.stderr)
    if failed:
        print(f"ERROR: Failed: {', '.join(failed)}", file=sys.stderr)
        return False
    
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            verbose = '--verbose' in sys.argv
            success = validate_all(verbose)
        else:
            verbose = '--verbose' in sys.argv
            success = validate_library(sys.argv[1], verbose)
    else:
        print("Usage: validate_library.py <name> [--verbose]", file=sys.stderr)
        print("       validate_library.py --all [--verbose]", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0 if success else 1)