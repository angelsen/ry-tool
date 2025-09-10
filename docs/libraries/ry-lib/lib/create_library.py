#!/usr/bin/env python3
"""Create a new ry-next library with proper structure."""

import os
from pathlib import Path
from ry_tool.utils import LibraryBase, validate_name, get_current_datetime, get_current_date


class LibraryCreator(LibraryBase):
    """Handle library creation with shared utilities."""
    
    def create_library(self, name: str, lib_type: str = 'utility', target: str = '') -> bool:
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
            self.error_message(f"Invalid library name: {name}")
            print("   Use only letters, numbers, hyphens, and underscores")
            return False
        
        # Check if library already exists
        if self.library_exists(name):
            self.error_message(f"Library {name} already exists")
            return False
    
        try:
            lib_dir = self.get_library_dir(name)
            lib_dir.mkdir(parents=True)
            (lib_dir / 'lib').mkdir()
        
            # Create library.yaml
            lib_config = {
                'version': '2.0',
                'name': name,
                'type': lib_type,
                'description': f'{name.replace("-", " ").title()} library for ry-next',
                'commands': {}
            }
        
            if lib_type == 'augmentation' and target:
                lib_config['target'] = target
        
            # Add example command based on type
            if lib_type == 'augmentation':
                lib_config['commands']['example'] = {
                    'description': 'Example augmentation command',
                    'relay': 'native',
                    'augment': {
                        'before': [
                            {'shell': f'echo "[{name}] Augmenting command..." >&2'}
                        ]
                    }
                }
            else:
                lib_config['commands']['hello'] = {
                    'description': 'Example command',
                    'execute': [
                        {'shell': f'echo "Hello from {name}!"'}
                    ]
                }
        
            # Save library config
            self.file_manager.save_yaml(lib_config, self.get_library_yaml(name))
        
            # Create meta.yaml
            meta = {
                'name': name,
                'version': '0.1.0',
                'description': lib_config['description'],
                'author': os.environ.get('USER', 'unknown'),
                'created': get_current_datetime(),
                'updated': get_current_date()
            }
            
            self.file_manager.save_yaml(meta, self.get_meta_yaml(name))
        
            # Create README.md
            readme = f"""# {name}

{lib_config['description']}

## Installation

```bash
ry-next --install {name}
```

## Usage

```bash
ry-next {name} --ry-help
```

## Commands

See `{name}.yaml` for available commands.

## Development

This library was created with ry-lib:
```bash
ry-next ry-lib init {name} --type {lib_type}
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
        
            self.success_message(f"Created library: {name}")
            print(f"   Type: {lib_type}")
            print(f"   Location: {lib_dir}")
            print(f"\n📝 Next steps:")
            print(f"   1. Edit {lib_dir}/{name}.yaml to add commands")
            print(f"   2. Test with: ry-next {name} --ry-help")
            print(f"   3. Install with: ry-next --install {name}")
            
            return True
        
        except Exception as e:
            self.error_message(f"Failed to create library: {e}")
            return False


# Direct usage: creator = LibraryCreator(); creator.create_library(name, type, target)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: create_library.py <name> [type] [target]")
        sys.exit(1)
    
    name = sys.argv[1]
    lib_type = sys.argv[2] if len(sys.argv) > 2 else 'utility'
    target = sys.argv[3] if len(sys.argv) > 3 else ''
    
    creator = LibraryCreator()
    success = creator.create_library(name, lib_type, target)
    sys.exit(0 if success else 1)