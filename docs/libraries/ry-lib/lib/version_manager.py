#!/usr/bin/env python3
"""Version management for ry-next libraries."""

import sys
import yaml
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple


def load_yaml(file_path: Path) -> Optional[dict]:
    """Load YAML file."""
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def save_yaml(data: dict, file_path: Path) -> bool:
    """Save YAML file."""
    try:
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception:
        return False


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse semantic version string."""
    parts = version_str.split('.')
    return (
        int(parts[0]) if len(parts) > 0 else 0,
        int(parts[1]) if len(parts) > 1 else 0,
        int(parts[2]) if len(parts) > 2 else 0
    )


def bump_semver(version: str, bump_type: str = 'patch') -> str:
    """Bump semantic version."""
    major, minor, patch = parse_version(version)
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def bump_version(library: str, bump_type: str = 'patch', message: str = '') -> bool:
    """
    Bump library version.
    
    Args:
        library: Library name
        bump_type: Type of bump (major, minor, patch)
        message: Optional changelog message
    
    Returns:
        True if successful, False otherwise
    """
    # Find library directory
    lib_dir = None
    for base in [Path('docs/libraries'), Path('libraries')]:
        if (base / library).exists():
            lib_dir = base / library
            break
    
    if not lib_dir:
        print(f"❌ Library {library} not found", file=sys.stderr)
        return False
    
    try:
        # Load current metadata
        meta_path = lib_dir / 'meta.yaml'
        if not meta_path.exists():
            print(f"❌ No meta.yaml found for {library}", file=sys.stderr)
            return False
        
        meta = load_yaml(meta_path)
        if not meta:
            print(f"❌ Could not load metadata for {library}", file=sys.stderr)
            return False
        
        # Bump version
        old_version = meta.get('version', '0.0.0')
        new_version = bump_semver(old_version, bump_type)
        meta['version'] = new_version
        
        # Update the updated date
        from datetime import date
        meta['updated'] = date.today().isoformat()
        
        # Save updated metadata
        if not save_yaml(meta, meta_path):
            print(f"❌ Failed to save meta.yaml", file=sys.stderr)
            return False
        
        # Update CHANGELOG if it exists and message provided
        changelog_file = lib_dir / 'CHANGELOG.md'
        if changelog_file.exists() and message:
            update_changelog(changelog_file, new_version, message)
        
        print(f"✅ Bumped {library}: {old_version} → {new_version}", file=sys.stderr)
        if message:
            print(f"   {message}", file=sys.stderr)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to bump version: {e}", file=sys.stderr)
        return False


def update_changelog(changelog_file: Path, version: str, message: str):
    """Update CHANGELOG.md with new version entry."""
    from datetime import date
    
    with open(changelog_file) as f:
        content = f.read()
    
    # Find where to insert new version
    lines = content.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('## '):
            insert_idx = i
            break
    
    # Create new entry
    new_entry = f"\n## [{version}] - {date.today()}\n\n### Changed\n- {message}\n"
    lines.insert(insert_idx, new_entry)
    
    with open(changelog_file, 'w') as f:
        f.write('\n'.join(lines))


def check_version_changes() -> bool:
    """
    Check if changed libraries have version bumps.
    Used for git pre-commit hooks.
    
    Returns:
        True if all changed libraries have version bumps, False otherwise
    """
    try:
        # Get changed files
        result = subprocess.run(
            ['/usr/bin/git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            check=True
        )
        changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    except Exception:
        print("❌ Not in a git repository", file=sys.stderr)
        return True
    
    # Check which libraries have changes
    changed_libs = set()
    for file in changed_files:
        # Check if file is in a library
        if 'libraries/' in file:
            parts = file.split('/')
            for i, part in enumerate(parts):
                if part == 'libraries' and i + 1 < len(parts):
                    changed_libs.add(parts[i + 1])
                    break
    
    # Check if meta.yaml has version bump for each changed library
    missing_bumps = []
    for lib in changed_libs:
        if f'libraries/{lib}/meta.yaml' not in changed_files:
            missing_bumps.append(lib)
    
    if missing_bumps:
        print("❌ Libraries changed without version bump:", file=sys.stderr)
        for lib in missing_bumps:
            print(f"   - {lib}", file=sys.stderr)
        print("📝 Run: ry-next ry-lib bump <library> --type patch", file=sys.stderr)
        return False
    
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check':
            success = check_version_changes()
        else:
            library = sys.argv[1]
            bump_type = sys.argv[2] if len(sys.argv) > 2 else 'patch'
            message = sys.argv[3] if len(sys.argv) > 3 else ''
            success = bump_version(library, bump_type, message)
    else:
        print("Usage: version_manager.py <library> [type] [message]", file=sys.stderr)
        print("       version_manager.py --check", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0 if success else 1)