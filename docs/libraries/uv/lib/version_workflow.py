#!/usr/bin/env python3
"""Version management workflows for uv."""

import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, Tuple


def get_current_version(package: Optional[str] = None) -> Tuple[str, str]:
    """
    Get current version info from uv.
    
    Args:
        package: Optional package name for workspace
    
    Returns:
        (version, package_name)
    """
    cmd = ['/usr/bin/uv', 'version', '--output-format', 'json']
    if package:
        cmd.extend(['--package', package])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get version: {result.stderr}")
    
    data = json.loads(result.stdout)
    return data['version'], data['package_name']


def check_git_clean() -> bool:
    """Check if git working directory is clean."""
    result = subprocess.run(
        ['/usr/bin/git', 'status', '--porcelain'],
        capture_output=True,
        text=True
    )
    return len(result.stdout.strip()) == 0


def check_changelog_exists(package: Optional[str] = None) -> Path:
    """
    Check if CHANGELOG.md exists.
    
    Args:
        package: Optional package name for workspace
    
    Returns:
        Path to changelog or None
    """
    if package:
        # Check package-specific changelog
        changelog = Path(f'packages/{package}/CHANGELOG.md')
        if changelog.exists():
            return changelog
    
    # Check root changelog
    changelog = Path('CHANGELOG.md')
    if changelog.exists():
        return changelog
    
    return None


def bump_version(bump_type: str, package: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Bump version using uv.
    
    Args:
        bump_type: Type of bump (major, minor, patch)
        package: Optional package name
    
    Returns:
        (old_version, new_version, package_name)
    """
    # Get current version
    old_version, package_name = get_current_version(package)
    
    # Bump version
    cmd = ['/usr/bin/uv', 'version', '--bump', bump_type]
    if package:
        cmd.extend(['--package', package])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to bump version: {result.stderr}")
    
    # Get new version
    new_version, _ = get_current_version(package)
    
    return old_version, new_version, package_name


def release_changelog(version: str, changelog_path: Path) -> bool:
    """
    Release version in changelog.
    
    Args:
        version: Version to release
        changelog_path: Path to CHANGELOG.md
    
    Returns:
        True if successful
    """
    result = subprocess.run(
        ['ry-next', 'changelog', 'release', version],
        cwd=changelog_path.parent,
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def commit_version_bump(package_name: str, old_version: str, new_version: str):
    """
    Commit version bump changes.
    
    Args:
        package_name: Name of package
        old_version: Previous version
        new_version: New version
    """
    # Stage all changes
    subprocess.run(['/usr/bin/git', 'add', '-A'], check=True)
    
    # Commit
    message = f"chore({package_name}): bump version from {old_version} to {new_version}"
    subprocess.run(['/usr/bin/git', 'commit', '-m', message], check=True)
    
    # Tag
    tag_name = f"{package_name}-v{new_version}"
    tag_message = f"Release {package_name} v{new_version}"
    subprocess.run(['/usr/bin/git', 'tag', tag_name, '-m', tag_message], check=True)
    
    print(f"✅ Committed and tagged as {tag_name}", file=sys.stderr)
    print(f"   Push with:", file=sys.stderr)
    print(f"     git push origin main", file=sys.stderr)
    print(f"     git push origin {tag_name}", file=sys.stderr)


def check_publish_requirements(package: Optional[str] = None) -> Tuple[bool, str]:
    """
    Check if ready to publish.
    
    Args:
        package: Optional package name
    
    Returns:
        (is_ready, error_message)
    """
    # Check for dist files
    dist_dir = Path(f'packages/{package}/dist' if package else 'dist')
    if not dist_dir.exists() or not list(dist_dir.glob('*')):
        return False, f"No dist files found. Run: uv build"
    
    # Get version from dist files
    version = None
    package_name = None
    
    for file in dist_dir.glob('*.whl'):
        # Extract from wheel filename
        parts = file.stem.split('-')
        if len(parts) >= 2:
            package_name = parts[0]
            version = parts[1]
            break
    
    if not version:
        for file in dist_dir.glob('*.tar.gz'):
            # Extract from sdist
            stem = file.stem
            if stem.endswith('.tar'):
                stem = stem[:-4]
            parts = stem.rsplit('-', 1)
            if len(parts) == 2:
                package_name = parts[0]
                version = parts[1]
                break
    
    if not version or not package_name:
        return False, "Could not determine version from dist files"
    
    # Check if version is tagged
    tag = f"{package_name}-v{version}"
    result = subprocess.run(
        ['/usr/bin/git', 'tag', '-l', tag],
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        return False, f"Version {version} not tagged. Expected tag: {tag}"
    
    # Check if tag is pushed
    result = subprocess.run(
        ['/usr/bin/git', 'ls-remote', '--tags', 'origin'],
        capture_output=True,
        text=True
    )
    
    if f"refs/tags/{tag}" not in result.stdout:
        return False, f"Tag {tag} not pushed. Run: git push origin {tag}"
    
    return True, ""


if __name__ == "__main__":
    # Test functions
    try:
        version, name = get_current_version()
        print(f"Current version: {name} {version}")
        
        if check_git_clean():
            print("Git working directory is clean")
        else:
            print("Git working directory has changes")
        
        changelog = check_changelog_exists()
        if changelog:
            print(f"Changelog found: {changelog}")
    except Exception as e:
        print(f"Error: {e}")