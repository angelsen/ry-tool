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
        print("❌ CHANGELOG.md already exists")
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
        print(f"✅ Created CHANGELOG.md")
        print("   Edit it manually to add your changes")
        return True
    except Exception as e:
        print(f"❌ Failed to create changelog: {e}")
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
        print("❌ CHANGELOG.md not found")
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
            print("❌ No [Unreleased] section found")
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
        
        print(f"✅ Released version {version}")
        print("   New [Unreleased] section added for next changes")
        return True
        
    except Exception as e:
        print(f"❌ Failed to release version: {e}")
        return False


def validate_changelog() -> bool:
    """
    Validate CHANGELOG.md format.
    
    Returns:
        True if valid
    """
    changelog_path = Path('CHANGELOG.md')
    
    if not changelog_path.exists():
        print("❌ CHANGELOG.md not found")
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
            print("❌ Validation failed:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        print("✅ CHANGELOG.md is valid")
        if sections_found:
            print(f"   Sections found: {', '.join(sections_found)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to validate: {e}")
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