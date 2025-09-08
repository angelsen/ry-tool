#!/usr/bin/env python3
"""Check if library versions need bumping based on git changes."""

import subprocess
import pathlib
import yaml
from typing import Set, Dict


def get_changed_libraries() -> Set[str]:
    """Get list of libraries with staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        
        changed_libs = set()
        for file in result.stdout.strip().split('\n'):
            if file.startswith("docs/libraries/"):
                parts = file.split('/')
                if len(parts) >= 3:
                    lib_name = parts[2]
                    changed_libs.add(lib_name)
        
        return changed_libs
    except subprocess.CalledProcessError:
        return set()


def get_version_changes() -> Dict[str, bool]:
    """Check which libraries had their meta.yaml version changed."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        
        version_changed = {}
        for file in result.stdout.strip().split('\n'):
            if file.endswith("/meta.yaml") and file.startswith("docs/libraries/"):
                # Check if version field was modified
                diff_result = subprocess.run(
                    ["git", "diff", "--cached", file],
                    capture_output=True,
                    text=True
                )
                
                lib_name = file.split('/')[2]
                # Simple check: if 'version:' appears in the diff, version was changed
                version_changed[lib_name] = "version:" in diff_result.stdout
        
        return version_changed
    except subprocess.CalledProcessError:
        return {}


def check_all_versions() -> bool:
    """Check if all changed libraries have version bumps."""
    changed_libs = get_changed_libraries()
    
    if not changed_libs:
        print("✅ No library changes to check")
        return True
    
    version_changes = get_version_changes()
    
    missing_bumps = []
    for lib in changed_libs:
        # Skip checking ry-dev itself during development
        if lib == "ry-dev":
            continue
            
        if not version_changes.get(lib, False):
            missing_bumps.append(lib)
    
    if missing_bumps:
        print("❌ Libraries changed without version bump:")
        for lib in missing_bumps:
            print(f"  - {lib}")
        print("\nRun: ry ry-dev bump <library> [patch|minor|major]")
        return False
    
    print("✅ All changed libraries have version bumps")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if check_all_versions() else 1)