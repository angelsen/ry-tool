#!/usr/bin/env python3
"""Build registry.json for all ry-next libraries."""

import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional


def build_registry(output_path: Optional[str] = None, pretty: bool = False) -> bool:
    """
    Generate registry.json for all libraries.
    
    Args:
        output_path: Output file path
        pretty: Pretty print JSON
    
    Returns:
        True if successful, False otherwise
    """
    # Find libraries directory
    libs_dir = None
    for path in [Path('docs/libraries'), Path('libraries')]:
        if path.exists():
            libs_dir = path
            break
    
    if not libs_dir:
        print("ERROR: No libraries directory found", file=sys.stderr)
        return False
    
    registry = {
        'version': '2.0',
        'generated': datetime.now().isoformat(),
        'libraries': {}
    }
    
    for lib_dir in sorted(libs_dir.iterdir()):
        if not lib_dir.is_dir():
            continue
        
        yaml_file = lib_dir / f'{lib_dir.name}.yaml'
        meta_file = lib_dir / 'meta.yaml'
        
        if yaml_file.exists():
            try:
                with open(yaml_file) as f:
                    lib_data = yaml.safe_load(f)
                
                entry = {
                    'type': lib_data.get('type', 'utility'),
                    'description': lib_data.get('description', ''),
                    'commands': list(lib_data.get('commands', {}).keys())
                }
                
                # Add metadata if available
                if meta_file.exists():
                    with open(meta_file) as f:
                        meta = yaml.safe_load(f)
                    if meta:
                        entry['version'] = meta.get('version', '0.0.0')
                        entry['author'] = meta.get('author', 'unknown')
                        entry['updated'] = meta.get('updated', '')
                
                registry['libraries'][lib_dir.name] = entry
                
            except Exception as e:
                print(f"WARNING: Skipping {lib_dir.name}: {e}", file=sys.stderr)
    
    # Determine output path
    if not output_path:
        output_path = libs_dir / 'registry.json'
    else:
        output_path = Path(output_path)
    
    try:
        with open(output_path, 'w') as f:
            if pretty:
                json.dump(registry, f, indent=2, sort_keys=True)
            else:
                json.dump(registry, f)
        
        print(f"SUCCESS: Generated registry with {len(registry['libraries'])} libraries", file=sys.stderr)
        print(f"   Written to: {output_path}", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to write registry: {e}", file=sys.stderr)
        return False


def list_libraries(as_json: bool = False, installed_only: bool = False) -> bool:
    """
    List available libraries.
    
    Args:
        as_json: Output as JSON
        installed_only: Show only installed libraries
    
    Returns:
        True if successful
    """
    if installed_only:
        # Check user installation directory
        user_dir = Path.home() / '.local' / 'share' / 'ry-next' / 'libraries'
        if user_dir.exists():
            installed = {}
            for lib_dir in user_dir.iterdir():
                if lib_dir.is_dir():
                    yaml_file = lib_dir / f'{lib_dir.name}.yaml'
                    if yaml_file.exists():
                        with open(yaml_file) as f:
                            data = yaml.safe_load(f)
                        installed[lib_dir.name] = {
                            'type': data.get('type', 'unknown'),
                            'version': '0.0.0'
                        }
            
            if as_json:
                print(json.dumps(installed, indent=2))  # Data output to stdout
            else:
                print("INFO: Installed Libraries:", file=sys.stderr)
                print("-" * 60, file=sys.stderr)
                for name, info in installed.items():
                    print(f"{name:20} {info.get('version', '0.0.0'):10} {info.get('type', 'unknown')}", file=sys.stderr)
        else:
            print("INFO: No libraries installed", file=sys.stderr)
        
        return True
    
    # List all available libraries
    libs_dir = None
    for path in [Path('docs/libraries'), Path('libraries')]:
        if path.exists():
            libs_dir = path
            break
    
    if not libs_dir:
        print("ERROR: No libraries directory found", file=sys.stderr)
        return False
    
    libraries = {}
    for lib_dir in sorted(libs_dir.iterdir()):
        if lib_dir.is_dir():
            yaml_file = lib_dir / f'{lib_dir.name}.yaml'
            if yaml_file.exists():
                try:
                    with open(yaml_file) as f:
                        data = yaml.safe_load(f)
                    
                    libraries[lib_dir.name] = {
                        'type': data.get('type', 'unknown'),
                        'version': '2.0',
                        'description': data.get('description', '')
                    }
                    
                    # Add version from meta if exists
                    meta_file = lib_dir / 'meta.yaml'
                    if meta_file.exists():
                        with open(meta_file) as f:
                            meta = yaml.safe_load(f)
                        if meta:
                            libraries[lib_dir.name]['version'] = meta.get('version', '0.0.0')
                    
                except Exception as e:
                    print(f"WARNING: Error reading {lib_dir.name}: {e}", file=sys.stderr)
    
    if as_json:
        print(json.dumps(libraries, indent=2))  # Data output to stdout
    else:
        if libraries:
            print("INFO: Available Libraries:", file=sys.stderr)
            print("-" * 80, file=sys.stderr)
            print(f"{'Name':20} {'Version':10} {'Type':12} Description", file=sys.stderr)
            print("-" * 80, file=sys.stderr)
            for name, info in libraries.items():
                desc = info['description'][:45] + '...' if len(info['description']) > 45 else info['description']
                print(f"{name:20} {info['version']:10} {info['type']:12} {desc}", file=sys.stderr)
        else:
            print("INFO: No libraries found", file=sys.stderr)
    
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            as_json = '--json' in sys.argv
            installed_only = '--installed' in sys.argv
            success = list_libraries(as_json, installed_only)
        else:
            output_path = sys.argv[1] if sys.argv[1] != '--pretty' else None
            pretty = '--pretty' in sys.argv
            success = build_registry(output_path, pretty)
    else:
        # Default: build registry
        success = build_registry(pretty=True)
    
    sys.exit(0 if success else 1)