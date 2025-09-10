#!/usr/bin/env python3
"""Version management workflows for uv."""

import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, Tuple
from workspace_utils import (
    get_package_info,
    get_package_location,
    get_workspace_info,
    validate_package_arg,
    check_git_clean
)


def get_current_version(package: Optional[str] = None) -> Tuple[str, str]:
    """
    Get current version info.
    First tries to read from pyproject.toml, falls back to uv if needed.
    
    Args:
        package: Optional package name for workspace
    
    Returns:
        (version, package_name)
    """
    # Try to get from tomllib first
    info = get_package_info(package)
    if info:
        # Extract package name from the info
        workspace = get_workspace_info()
        if package:
            package_name = package
        else:
            package_name = workspace['root_package']
        
        return info['version'], package_name
    
    # Fallback to uv command if tomllib fails
    cmd = ['/usr/bin/uv', 'version', '--output-format', 'json']
    if package:
        cmd.extend(['--package', package])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get version: {result.stderr}")
    
    data = json.loads(result.stdout)
    return data['version'], data['package_name']


def check_changelog_exists(package: Optional[str] = None) -> Optional[Path]:
    """
    Check if CHANGELOG.md exists.
    Uses workspace info to find correct location for nested packages.
    
    Args:
        package: Optional package name for workspace
    
    Returns:
        Path to changelog or None
    """
    if package:
        # Get actual package location from workspace config
        package_dir = get_package_location(package)
        if package_dir:
            changelog = package_dir / 'CHANGELOG.md'
            if changelog.exists():
                return changelog
        # If package specified but not found in workspace, that's an error condition
        # Don't look for random directories, let caller handle the None return
    
    # Check root changelog (for root package or as fallback)
    changelog = Path('CHANGELOG.md')
    if changelog.exists():
        return changelog
    
    return None


def release_changelog(version: str, changelog_path: Path) -> bool:
    """
    Release version in changelog.
    
    Args:
        version: Version to release
        changelog_path: Path to CHANGELOG.md
    
    Returns:
        True if successful
    """
    # Import directly from changelog library
    from changelog_core import release_version
    return release_version(version, None)  # None for date means today


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
    
    print(f"SUCCESS: Committed and tagged as {tag_name}", file=sys.stderr)
    print(f"INFO: Next steps:", file=sys.stderr)
    print(f"   1. git push origin main", file=sys.stderr)
    print(f"   2. git push origin {tag_name}", file=sys.stderr)


def check_publish_requirements(package: Optional[str] = None) -> Tuple[bool, str]:
    """
    Check if ready to publish.
    Uses workspace info to validate package and check requirements.
    
    Args:
        package: Optional package name
    
    Returns:
        (is_ready, error_message)
    """
    # Validate package exists and get its info
    if package:
        valid_package = validate_package_arg(package)
        if not valid_package:
            return False, f"Unknown package: {package}"
        package_name = valid_package
    else:
        # Get root package
        workspace = get_workspace_info()
        if not workspace or not workspace['root_package']:
            return False, "Could not determine root package"
        package_name = workspace['root_package']
    
    # Get version info
    try:
        version, _ = get_current_version(package_name if package else None)
    except Exception as e:
        return False, f"Could not get version info: {e}"
    
    # Check for dist files in package-specific directory
    dist_dir = Path(f'dist/{package_name}')
    if not dist_dir.exists() or not list(dist_dir.glob('*')):
        build_cmd = f"uv build --package {package_name}" if package else "uv build"
        return False, f"No dist files found in {dist_dir}. Run: ry {build_cmd}"
    
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
        print(f"Current version: {name} {version}", file=sys.stderr)
        
        if check_git_clean():
            print("Git working directory is clean", file=sys.stderr)
        else:
            print("Git working directory has changes", file=sys.stderr)
        
        changelog = check_changelog_exists()
        if changelog:
            print(f"Changelog found: {changelog}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)