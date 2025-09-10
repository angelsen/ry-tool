#!/usr/bin/env python3
"""Workspace utilities for uv library using tomllib."""

import os
import sys
import subprocess
import tomllib
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Cache workspace info to avoid re-reading
_workspace_cache = None


def get_workspace_info() -> Optional[Dict]:
    """
    Get workspace configuration from pyproject.toml.
    Results are cached for performance.
    """
    global _workspace_cache
    if _workspace_cache is not None:
        return _workspace_cache
    
    try:
        with open('pyproject.toml', 'rb') as f:
            data = tomllib.load(f)
        
        project = data.get('project', {})
        workspace = data.get('tool', {}).get('uv', {}).get('workspace', {})
        
        _workspace_cache = {
            'is_workspace': bool(workspace.get('members')),
            'members': workspace.get('members', []),
            'root_package': project.get('name'),
            'root_version': project.get('version', '0.0.0')
        }
        
        return _workspace_cache
    except FileNotFoundError:
        print("ERROR: No pyproject.toml found", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Failed to read pyproject.toml: {e}", file=sys.stderr)
        return None


def get_all_packages() -> Dict[str, Dict]:
    """
    Get all packages (root + workspace members) with their info.
    
    Returns:
        Dict mapping package name to info dict containing:
        - location: Path to package directory
        - version: Package version
        - is_workspace_member: Boolean
        - pyproject_path: Path to package's pyproject.toml
    """
    packages = {}
    workspace = get_workspace_info()
    
    if not workspace:
        return packages
    
    # Add root package
    if workspace['root_package']:
        packages[workspace['root_package']] = {
            'location': Path('.'),
            'version': workspace['root_version'],
            'is_workspace_member': False,
            'pyproject_path': Path('pyproject.toml')
        }
    
    # Add workspace members
    for member in workspace['members']:
        member_path = Path(member)
        member_toml = member_path / 'pyproject.toml'
        
        if member_toml.exists():
            try:
                with open(member_toml, 'rb') as f:
                    data = tomllib.load(f)
                    project = data.get('project', {})
                    pkg_name = project.get('name')
                    
                    if pkg_name:
                        packages[pkg_name] = {
                            'location': member_path,
                            'version': project.get('version', '0.0.0'),
                            'is_workspace_member': True,
                            'pyproject_path': member_toml
                        }
            except Exception as e:
                # Use directory name as fallback
                pkg_name = member.split('/')[-1]
                packages[pkg_name] = {
                    'location': member_path,
                    'version': '0.0.0',
                    'is_workspace_member': True,
                    'pyproject_path': member_toml
                }
    
    return packages


def get_package_location(package_name: str) -> Optional[Path]:
    """
    Get the actual directory location of a package.
    
    Args:
        package_name: Name of the package
    
    Returns:
        Path to package directory or None if not found
    """
    packages = get_all_packages()
    if package_name in packages:
        return packages[package_name]['location']
    return None


def validate_package_arg(package: str) -> Optional[str]:
    """
    Validate and normalize package argument.
    Handles both package names and paths.
    
    Args:
        package: Package name or path
    
    Returns:
        Normalized package name or None if invalid
    """
    packages = get_all_packages()
    
    # Direct match by name
    if package in packages:
        return package
    
    # Check if it's a path that matches a workspace member
    for pkg_name, info in packages.items():
        if str(info['location']) == package or str(info['location']) == package.rstrip('/'):
            return pkg_name
    
    # Package not found
    return None


def get_package_name_from_path(file_path: str) -> Optional[str]:
    """
    Extract package name from a dist file path.
    
    Args:
        file_path: Path like "dist/backend/*" or "dist/some-package/*"
    
    Returns:
        Package name or None if not determinable
    """
    if 'dist/' not in file_path:
        return None
    
    # Extract the part after dist/
    parts = file_path.split('/')
    if len(parts) >= 2:
        idx = parts.index('dist')
        if idx + 1 < len(parts):
            potential_pkg = parts[idx + 1].rstrip('*')
            
            # Validate against actual packages
            packages = get_all_packages()
            if potential_pkg in packages:
                return potential_pkg
    
    return None


def list_built_packages() -> List[Tuple[str, Path]]:
    """
    List all packages that have been built (have dist directories).
    
    Returns:
        List of (package_name, dist_path) tuples
    """
    dist_dir = Path('dist')
    if not dist_dir.exists():
        return []
    
    built = []
    packages = get_all_packages()
    
    for subdir in dist_dir.iterdir():
        if subdir.is_dir() and subdir.name in packages:
            # Check if it has actual build artifacts
            if list(subdir.glob('*.whl')) or list(subdir.glob('*.tar.gz')):
                built.append((subdir.name, subdir))
    
    return built


def get_package_info(package: Optional[str] = None) -> Optional[Dict]:
    """
    Get detailed info for a specific package.
    
    Args:
        package: Package name (None for root package)
    
    Returns:
        Package info dict or None if not found
    """
    packages = get_all_packages()
    
    if package:
        return packages.get(package)
    else:
        # Return root package
        workspace = get_workspace_info()
        if workspace and workspace['root_package']:
            return packages.get(workspace['root_package'])
    
    return None


def show_available_packages(invalid_package: str = None) -> None:
    """
    Show available packages when an invalid package is specified.
    
    Args:
        invalid_package: The invalid package name that was provided
    """
    packages = get_all_packages()
    
    if invalid_package:
        print(f"ERROR: Unknown package '{invalid_package}'", file=sys.stderr)
    
    if not packages:
        print("ERROR: No packages found in project", file=sys.stderr)
        return
    
    print("", file=sys.stderr)
    print("Available packages:", file=sys.stderr)
    for pkg_name, info in packages.items():
        location = str(info['location'])
        if location == '.':
            print(f"  - {pkg_name} (root)", file=sys.stderr)
        else:
            print(f"  - {pkg_name} (in {location}/)", file=sys.stderr)


def is_workspace_project() -> bool:
    """Check if current directory is a workspace project."""
    workspace = get_workspace_info()
    return workspace is not None and workspace.get('is_workspace', False)


def show_workspace_status() -> None:
    """Print workspace status and available packages."""
    workspace = get_workspace_info()
    
    if not workspace:
        print("ERROR: Not in a Python project (no pyproject.toml)", file=sys.stderr)
        return
    
    packages = get_all_packages()
    built = list_built_packages()
    built_names = {name for name, _ in built}
    
    if workspace['is_workspace']:
        print(f"Workspace project: {workspace['root_package']}", file=sys.stderr)
        print(f"Members: {len(workspace['members'])}", file=sys.stderr)
    else:
        print(f"Single package project: {workspace['root_package']}", file=sys.stderr)
    
    print("", file=sys.stderr)
    print("Packages:", file=sys.stderr)
    
    for pkg_name, info in packages.items():
        status = "[built]" if pkg_name in built_names else "[not built]"
        location = str(info['location']) if str(info['location']) != '.' else "root"
        version = info['version']
        print(f"  - {pkg_name} v{version} [{location}] {status}", file=sys.stderr)


def validate_and_normalize_package_flag(flags: Dict) -> Optional[str]:
    """
    Validate package flag and update flags dict, exit on error.
    
    Args:
        flags: Command flags dictionary
    
    Returns:
        Normalized package name or None if no package specified
    """
    package = flags.get('package')
    if package:
        valid_package = validate_package_arg(package)
        if not valid_package:
            show_available_packages(package)
            sys.exit(1)
        flags['package'] = valid_package
        return valid_package
    return None


def check_git_clean() -> bool:
    """
    Check if git working directory is clean.
    
    Returns:
        True if clean, False if dirty
    """
    import subprocess
    result = subprocess.run(
        ['/usr/bin/git', 'status', '--porcelain'],
        capture_output=True,
        text=True
    )
    return len(result.stdout.strip()) == 0


def ensure_git_clean(warning_only: bool = False) -> None:
    """
    Ensure git working directory is clean or show appropriate message.
    
    Args:
        warning_only: If True, show warning instead of error for dirty tree
    """
    if not check_git_clean():
        if warning_only:
            print("WARNING: Building from dirty working tree", file=sys.stderr)
        else:
            print("ERROR: Working directory not clean", file=sys.stderr)
            print("  Commit or stash changes first", file=sys.stderr)
            sys.exit(1)


def get_pypi_token() -> Optional[str]:
    """
    Get PyPI token from environment or pass.
    
    Returns:
        Token string or None if not available
    """
    import os
    import subprocess
    
    # Check environment first
    token = os.environ.get('UV_PUBLISH_TOKEN')
    if token:
        return token
    
    # Try to get from pass
    try:
        result = subprocess.run(
            ['pass', 'pypi/uv-publish'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("AUTH: Will use PyPI token from pass", file=sys.stderr)
            return result.stdout.strip()
    except FileNotFoundError:
        pass  # pass command not available
    
    print("WARNING: No UV_PUBLISH_TOKEN set and no token in pass", file=sys.stderr)
    print("  Set UV_PUBLISH_TOKEN or store with: pass insert pypi/uv-publish", file=sys.stderr)
    return None


def show_publish_help(built_packages: List[Tuple[str, Path]]) -> None:
    """
    Show help for publishing packages.
    
    Args:
        built_packages: List of (package_name, dist_path) tuples
    """
    if not built_packages:
        print("No packages have been built yet. Run build first:", file=sys.stderr)
        print("  uv build", file=sys.stderr)
        print("  uv build --all-packages", file=sys.stderr)
        print("  uv build --package PACKAGE", file=sys.stderr)
    else:
        print("", file=sys.stderr)
        print("Built packages available to publish:", file=sys.stderr)
        for pkg_name, dist_path in built_packages:
            whl_files = list(dist_path.glob('*.whl'))
            tar_files = list(dist_path.glob('*.tar.gz'))
            
            if whl_files or tar_files:
                print(f"  {pkg_name}:", file=sys.stderr)
                for f in whl_files[:1]:  # Show only first wheel
                    print(f"    uv publish {f}", file=sys.stderr)
                for f in tar_files[:1]:  # Show only first tarball
                    print(f"    uv publish {f}", file=sys.stderr)
        
        print("", file=sys.stderr)
        print("Or publish all files for a package:", file=sys.stderr)
        for pkg_name, dist_path in built_packages:
            print(f"  uv publish dist/{pkg_name}/*", file=sys.stderr)