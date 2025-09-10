#!/usr/bin/env python3
"""Build registry.json for all ry-next libraries."""

import sys
from pathlib import Path
import yaml
import json
from datetime import datetime


def build_registry(output_path: str = None, pretty: bool = False) -> bool:
    """
    Generate registry.json for all libraries.
    
    Args:
        output_path: Output file path (default: docs_next/libraries/registry.json)
        pretty: Pretty print JSON
    
    Returns:
        True if successful, False otherwise
    """
    libs_dir = Path('docs_next/libraries')
    if not libs_dir.exists():
        print("No libraries directory")
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
                
                if lib_data.get('type') == 'augmentation':
                    entry['target'] = lib_data.get('target', '')
                
                if meta_file.exists():
                    with open(meta_file) as f:
                        meta = yaml.safe_load(f)
                    entry['version'] = meta.get('version', '0.0.0')
                    entry['author'] = meta.get('author', 'unknown')
                else:
                    entry['version'] = '0.0.0'
                    entry['author'] = 'unknown'
                
                registry['libraries'][lib_dir.name] = entry
                
            except Exception as e:
                print(f"⚠️  Skipping {lib_dir.name}: {e}")
    
    # Write registry
    if not output_path:
        output_path = 'docs_next/libraries/registry.json'
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        indent = 2 if pretty else None
        with open(output_file, 'w') as f:
            json.dump(registry, f, indent=indent, sort_keys=True)
        
        print(f"📋 Generated registry with {len(registry['libraries'])} libraries")
        print(f"   Written to: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to write registry: {e}")
        return False


def list_libraries(as_json: bool = False, installed_only: bool = False) -> bool:
    """
    List all available libraries.
    
    Args:
        as_json: Output as JSON
        installed_only: Show only installed libraries
    
    Returns:
        True if successful
    """
    if installed_only:
        # Check installed libraries
        installed_file = Path.home() / '.local/share/ry-next/installed.json'
        if installed_file.exists():
            with open(installed_file) as f:
                installed = json.load(f)
            
            if as_json:
                print(json.dumps(installed, indent=2))
            else:
                print("Installed Libraries:")
                print("-" * 60)
                for name, info in installed.items():
                    print(f"{name:20} {info.get('version', '0.0.0'):10} {info.get('type', 'unknown')}")
        else:
            print("No libraries installed")
        return True
    
    # List all available libraries
    libs_dir = Path('docs_next/libraries')
    if not libs_dir.exists():
        print("No libraries directory found")
        return False
    
    libraries = {}
    
    for lib_dir in sorted(libs_dir.iterdir()):
        if lib_dir.is_dir():
            meta_file = lib_dir / 'meta.yaml'
            yaml_file = lib_dir / f'{lib_dir.name}.yaml'
            
            if yaml_file.exists():
                try:
                    with open(yaml_file) as f:
                        lib_data = yaml.safe_load(f)
                    
                    info = {
                        'type': lib_data.get('type', 'unknown'),
                        'description': lib_data.get('description', '')
                    }
                    
                    if meta_file.exists():
                        with open(meta_file) as f:
                            meta = yaml.safe_load(f)
                        info['version'] = meta.get('version', '0.0.0')
                        info['author'] = meta.get('author', 'unknown')
                    else:
                        info['version'] = '0.0.0'
                    
                    libraries[lib_dir.name] = info
                except Exception as e:
                    print(f"⚠️  Error reading {lib_dir.name}: {e}")
    
    if as_json:
        print(json.dumps(libraries, indent=2))
    else:
        if libraries:
            print("Available Libraries:")
            print("-" * 80)
            print(f"{'Name':20} {'Version':10} {'Type':12} Description")
            print("-" * 80)
            for name, info in libraries.items():
                desc = info['description'][:40] + '...' if len(info['description']) > 40 else info['description']
                print(f"{name:20} {info['version']:10} {info['type']:12} {desc}")
        else:
            print("No libraries found")
    
    return True


if __name__ == "__main__":
    # Can be run standalone for testing
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            as_json = '--json' in sys.argv
            installed = '--installed' in sys.argv
            success = list_libraries(as_json, installed)
        else:
            output = sys.argv[1] if sys.argv[1] != '--pretty' else None
            pretty = '--pretty' in sys.argv
            success = build_registry(output, pretty)
    else:
        success = build_registry(pretty=True)
    
    sys.exit(0 if success else 1)