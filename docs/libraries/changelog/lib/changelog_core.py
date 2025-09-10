#!/usr/bin/env python3
"""Core changelog operations - simple and dependency-free."""

import sys
from pathlib import Path
from datetime import date


def init_changelog(project_name: str = None) -> bool:
    """
    Initialize a new CHANGELOG.md file.
    
    Args:
        project_name: Optional project name for the title
    
    Returns:
        True if successful
    """
    changelog_path = Path('CHANGELOG.md')
    
    if changelog_path.exists():
        print("ERROR: CHANGELOG.md already exists", file=sys.stderr)
        return False
    
    title = f"# Changelog"
    if project_name:
        title = f"# Changelog - {project_name}"
    
    content = f"""{title}

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""
    
    try:
        with open(changelog_path, 'w') as f:
            f.write(content)
        print("SUCCESS: Created CHANGELOG.md", file=sys.stderr)
        print("INFO: Next: Edit CHANGELOG.md to add your changes", file=sys.stderr)
        return True
    except Exception as e:
        print(f"ERROR: Failed to create changelog: {e}", file=sys.stderr)
        return False


def release_version(version: str, release_date: str = None) -> bool:
    """
    Convert Unreleased section to a versioned release.
    
    Args:
        version: Version number (e.g., 1.0.0)
        release_date: Optional date (defaults to today)
    
    Returns:
        True if successful
    """
    changelog_path = Path('CHANGELOG.md')
    
    if not changelog_path.exists():
        print("ERROR: CHANGELOG.md not found", file=sys.stderr)
        print("   Run: ry-next changelog init", file=sys.stderr)
        return False
    
    if not release_date:
        release_date = date.today().isoformat()
    
    try:
        with open(changelog_path, 'r') as f:
            content = f.read()
        
        # Replace [Unreleased] with version
        old_header = '## [Unreleased]'
        new_header = f'## [{version}] - {release_date}'
        
        if old_header not in content:
            print("ERROR: No [Unreleased] section found", file=sys.stderr)
            print("   Add: ## [Unreleased] section to CHANGELOG.md", file=sys.stderr)
            return False
        
        # Replace the first occurrence
        content = content.replace(old_header, new_header, 1)
        
        # Add new Unreleased section at the top
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == new_header:
                # Insert new Unreleased before this version
                lines.insert(i, '')
                lines.insert(i, '## [Unreleased]')
                break
        
        with open(changelog_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"SUCCESS: Released version {version}", file=sys.stderr)
        print("INFO: Next: git add CHANGELOG.md && git commit -m 'chore: release v{version}'".format(version=version), file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to release version: {e}", file=sys.stderr)
        return False


def has_unreleased_content() -> bool:
    """
    Check if CHANGELOG has content under [Unreleased].
    
    Returns:
        True if has content, False otherwise
    """
    changelog_path = Path('CHANGELOG.md')
    
    if not changelog_path.exists():
        return False
    
    try:
        with open(changelog_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        in_unreleased = False
        
        for line in lines:
            if '## [Unreleased]' in line:
                in_unreleased = True
            elif in_unreleased:
                if line.startswith('## ['):
                    break
                # Check for actual content (not just headers or empty lines)
                if line.strip() and not line.startswith('#'):
                    return True
        
        return False
        
    except Exception:
        return False


def validate_changelog() -> bool:
    """
    Validate CHANGELOG.md format.
    
    Returns:
        True if valid
    """
    changelog_path = Path('CHANGELOG.md')
    
    if not changelog_path.exists():
        print("ERROR: CHANGELOG.md not found", file=sys.stderr)
        print("   Run: ry-next changelog init", file=sys.stderr)
        return False
    
    try:
        with open(changelog_path, 'r') as f:
            content = f.read()
        
        issues = []
        
        # Check for required elements
        if '# Changelog' not in content:
            issues.append("Missing '# Changelog' header")
        
        if '[Unreleased]' not in content:
            issues.append("Missing [Unreleased] section")
        
        # Check for valid sections
        valid_sections = ['Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security']
        sections_found = []
        for section in valid_sections:
            if f'### {section}' in content:
                sections_found.append(section)
        
        if issues:
            print("ERROR: Validation failed:", file=sys.stderr)
            for issue in issues:
                print(f"   - {issue}", file=sys.stderr)
            return False
        
        print("SUCCESS: CHANGELOG.md is valid", file=sys.stderr)
        if sections_found:
            print(f"INFO: Sections: {', '.join(sections_found)}", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to validate: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Test functions
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            init_changelog()
        elif sys.argv[1] == 'validate':
            validate_changelog()
        else:
            print("Usage: changelog_core.py [init|validate]")