#!/usr/bin/env python3
"""Validate ry-next library structure and content."""

from pathlib import Path
from ry_tool.utils import LibraryBase, handle_errors


class LibraryValidator(LibraryBase):
    """Handle library validation with shared utilities."""
    
    def validate_library(self, name: str, verbose: bool = False) -> bool:
        """
        Validate a specific library.
        
        Args:
            name: Library name to validate
            verbose: Show detailed information
        
        Returns:
            True if valid, False otherwise
        """
        if not self.library_exists(name):
            self.error_message(f"Library not found: {name}")
            return False
    
        try:
            # Load library configuration
            data = self.load_library_config(name)
            if not data:
                self.error_message(f"Could not load {name}.yaml")
                return False
            
            # Validate structure
            assert data.get('version') == '2.0', "Must be version 2.0"
            assert 'name' in data, "Missing name field"
            assert 'type' in data, "Missing type field"
            assert data['type'] in ['augmentation', 'utility', 'hybrid'], f"Invalid type: {data['type']}"
            
            if data['type'] == 'augmentation':
                # Check for target or relay commands
                has_target = 'target' in data
                has_relay = any('relay' in cmd for cmd in data.get('commands', {}).values())
                assert has_target or has_relay, "Augmentation library needs target or relay commands"
            
            # Check meta.yaml
            meta = self.load_library_meta(name)
            if meta:
                assert 'version' in meta, "meta.yaml missing version"
                assert 'name' in meta, "meta.yaml missing name"
            
            self.success_message(f"{name}: Valid")
            
            if verbose:
                print(f"   Version: {data.get('version')}")
                print(f"   Type: {data.get('type')}")
                print(f"   Commands: {len(data.get('commands', {}))}")
                if meta:
                    print(f"   Library version: {meta.get('version', '0.0.0')}")
            
            return True
            
        except AssertionError as e:
            self.error_message(f"{name}: {e}")
            return False
        except Exception as e:
            self.error_message(f"{name}: {e}")
            return False


    def validate_all(self, verbose: bool = False) -> bool:
        """
        Validate all libraries in docs_next/libraries.
        
        Args:
            verbose: Show detailed information
        
        Returns:
            True if all valid, False if any failed
        """
        libraries = self.list_libraries()
        if not libraries:
            self.info_message("No libraries found")
            return True
        
        failed = []
        validated = 0
        
        for lib_name in libraries:
            if self.validate_library(lib_name, verbose):
                validated += 1
            else:
                failed.append(lib_name)
        
        print(f"\n📊 Validated {validated} libraries")
        if failed:
            self.error_message(f"Failed: {', '.join(failed)}")
            return False
        
        return True


# Direct usage: validator = LibraryValidator(); validator.validate_library(name, verbose)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        validator = LibraryValidator()
        if sys.argv[1] == '--all':
            verbose = '--verbose' in sys.argv
            success = validator.validate_all(verbose)
        else:
            verbose = '--verbose' in sys.argv
            success = validator.validate_library(sys.argv[1], verbose)
    else:
        print("Usage: validate_library.py <name> [--verbose]")
        print("       validate_library.py --all [--verbose]")
        sys.exit(1)
    
    sys.exit(0 if success else 1)