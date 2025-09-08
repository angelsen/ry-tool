#!/usr/bin/env python3
"""Bump library versions following semver."""

import pathlib
import yaml
import re
import sys
from typing import Tuple
import datetime


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string to tuple of integers."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(map(int, match.groups()))


def bump_version(version: str, bump_type: str) -> str:
    """Bump version according to type (patch/minor/major)."""
    major, minor, patch = parse_version(version)
    
    if bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "major":
        return f"{major + 1}.0.0"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_changelog(lib_dir: pathlib.Path, old_version: str, new_version: str, bump_type: str):
    """Update library's CHANGELOG.md with new version."""
    changelog_file = lib_dir / "CHANGELOG.md"
    
    if not changelog_file.exists():
        print(f"  ⚠️  No CHANGELOG.md found for {lib_dir.name}")
        return
    
    content = changelog_file.read_text()
    today = datetime.date.today()
    
    # Check if there's an [Unreleased] section
    if '## [Unreleased]' in content:
        # Replace [Unreleased] with the new version and date
        content = content.replace('## [Unreleased]', f'## [{new_version}] - {today}')
        
        # Add a new [Unreleased] section at the top
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                # Insert new Unreleased section before the first version section
                lines.insert(i, '')
                lines.insert(i, '### Removed')
                lines.insert(i, '')
                lines.insert(i, '### Fixed')
                lines.insert(i, '')
                lines.insert(i, '### Changed')
                lines.insert(i, '')
                lines.insert(i, '### Added')
                lines.insert(i, '')
                lines.insert(i, '## [Unreleased]')
                break
        content = '\n'.join(lines)
    else:
        # No [Unreleased] section, just add new version
        new_section = f"\n## [{new_version}] - {today}\n\n### Changed\n- Version bump ({bump_type})\n"
        lines = content.split('\n')
        insert_idx = 0
        
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                insert_idx = i
                break
        
        if insert_idx == 0:
            # No existing version sections, add after header
            for i, line in enumerate(lines):
                if line.strip() == '':
                    insert_idx = i
                    break
        
        lines.insert(insert_idx, new_section)
        content = '\n'.join(lines)
    
    changelog_file.write_text(content)
    print(f"  ✅ Updated CHANGELOG.md")


def bump_library_version(lib_name: str, bump_type: str) -> bool:
    """Bump the version of a specific library."""
    # Check if bump_type is valid
    if bump_type not in ["patch", "minor", "major"]:
        print(f"ERROR: Invalid bump type '{bump_type}'", file=sys.stderr)
        print("  Valid types: patch, minor, major", file=sys.stderr)
        return False
    
    # Find library directory
    docs_dir = pathlib.Path.cwd() / "docs" / "libraries"
    lib_dir = docs_dir / lib_name
    
    if not lib_dir.exists():
        print(f"ERROR: Library '{lib_name}' not found", file=sys.stderr)
        print(f"  Looking in: {lib_dir}", file=sys.stderr)
        return False
    
    # Read current version
    meta_file = lib_dir / "meta.yaml"
    if not meta_file.exists():
        print(f"ERROR: No meta.yaml found for {lib_name}", file=sys.stderr)
        return False
    
    with open(meta_file) as f:
        meta = yaml.safe_load(f)
    
    old_version = meta.get("version", "0.1.0")
    
    # Bump version
    try:
        new_version = bump_version(old_version, bump_type)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False
    
    # Update meta.yaml
    meta["version"] = new_version
    with open(meta_file, "w") as f:
        yaml.dump(meta, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ {lib_name}: {old_version} → {new_version}")
    
    # Update CHANGELOG.md if it exists
    update_changelog(lib_dir, old_version, new_version, bump_type)
    
    # Also update version in main YAML if it's hardcoded there
    main_yaml = lib_dir / f"{lib_name}.yaml"
    if main_yaml.exists():
        content = main_yaml.read_text()
        # Replace version strings in echo commands
        content = content.replace(f'"{lib_name} version {old_version}"', 
                                f'"{lib_name} version {new_version}"')
        content = content.replace(f"'{lib_name} version {old_version}'", 
                                f"'{lib_name} version {new_version}'")
        main_yaml.write_text(content)
    
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: version_bumper.py <library> <patch|minor|major>")
        sys.exit(1)
    
    success = bump_library_version(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)