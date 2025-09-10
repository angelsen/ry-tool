#!/usr/bin/env python3
"""Create a new ry library with proper structure."""

import os
import sys
import yaml
from pathlib import Path
from typing import Optional


def validate_name(name: str) -> bool:
    """Validate library name."""
    import re
    return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name))


def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format."""
    from datetime import date
    return date.today().isoformat()


def get_current_datetime() -> str:
    """Get current datetime in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()


def create_library(name: str, lib_type: str = 'utility', target: str = '') -> bool:
    """
    Create a new library with all required files.
    
    Args:
        name: Library name
        lib_type: Type of library (augmentation, utility, hybrid)
        target: Target binary for augmentation libraries
    
    Returns:
        True if successful, False otherwise
    """
    # Validate name
    if not validate_name(name):
        print(f"ERROR: Invalid library name: {name}", file=sys.stderr)
        print("   Use only letters, numbers, hyphens, and underscores", file=sys.stderr)
        return False
    
    # Determine library directory
    base_path = Path('docs/libraries')
    if not base_path.exists():
        base_path = Path('libraries')
        if not base_path.exists():
            base_path.mkdir(parents=True)
    
    lib_dir = base_path / name
    
    # Check if library already exists
    if lib_dir.exists():
        print(f"ERROR: Library {name} already exists", file=sys.stderr)
        return False
    
    try:
        lib_dir.mkdir(parents=True)
        (lib_dir / 'lib').mkdir()
        
        # Load template based on type
        template_path = Path(__file__).parent / 'templates' / f'{lib_type}.yaml'
        if template_path.exists():
            with open(template_path) as f:
                template_content = f.read()
            
            # Replace template variables
            description = f'{name.replace("-", " ").title()} library for ry'
            template_content = template_content.replace('{{name}}', name)
            template_content = template_content.replace('{{description}}', description)
            if lib_type == 'augmentation' and target:
                template_content = template_content.replace('{{target}}', target)
            
            # Parse the templated YAML
            lib_config = yaml.safe_load(template_content)
        else:
            # Fallback to basic structure if template not found
            lib_config = {
                'version': '2.0',
                'name': name,
                'type': lib_type,
                'description': f'{name.replace("-", " ").title()} library for ry',
                'commands': {
                    'hello': {
                        'description': 'Example command',
                        'execute': [
                            {'shell': f'echo "Hello from {name}!" >&2'}
                        ]
                    }
                },
                'workflows': [
                    f'ry {name} hello     # Run example command'
                ]
            }
            if lib_type == 'augmentation' and target:
                lib_config['target'] = target
        
        # Save library config
        with open(lib_dir / f'{name}.yaml', 'w') as f:
            yaml.dump(lib_config, f, default_flow_style=False, sort_keys=False)
        
        # Create meta.yaml
        meta = {
            'name': name,
            'version': '0.1.0',
            'description': lib_config.get('description', ''),
            'author': os.environ.get('USER', 'unknown'),
            'created': get_current_datetime(),
            'updated': get_current_date()
        }
        
        with open(lib_dir / 'meta.yaml', 'w') as f:
            yaml.dump(meta, f, default_flow_style=False)
        
        # Create README.md
        readme = f"""# {name}

{lib_config.get('description', '')}

## Installation

```bash
ry --install {name}
```

## Usage

```bash
ry {name} --ry-help
```

## Commands

See `{name}.yaml` for available commands.

## Development

This library was created with ry-lib:
```bash
ry ry-lib init {name} --type {lib_type}
```
"""
        
        with open(lib_dir / 'README.md', 'w') as f:
            f.write(readme)
        
        # Create CHANGELOG.md
        changelog = f"""# Changelog - {name}

## [0.1.0] - {get_current_date()}

### Added
- Initial release
- Basic command structure
"""
        
        with open(lib_dir / 'CHANGELOG.md', 'w') as f:
            f.write(changelog)
        
        print(f"SUCCESS: Created library: {name}", file=sys.stderr)
        print(f"INFO: Type: {lib_type}", file=sys.stderr)
        print(f"   Location: {lib_dir}", file=sys.stderr)
        print(f"INFO: Next steps:", file=sys.stderr)
        print(f"   1. Edit {lib_dir}/{name}.yaml to add commands", file=sys.stderr)
        print(f"   2. Test with: ry {name} --ry-help", file=sys.stderr)
        print(f"   3. Install with: ry --install {name}", file=sys.stderr)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create library: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: create_library.py <name> [type] [target]", file=sys.stderr)
        sys.exit(1)
    
    name = sys.argv[1]
    lib_type = sys.argv[2] if len(sys.argv) > 2 else 'utility'
    target = sys.argv[3] if len(sys.argv) > 3 else ''
    
    success = create_library(name, lib_type, target)
    sys.exit(0 if success else 1)