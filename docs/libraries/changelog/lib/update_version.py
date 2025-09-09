"""Update changelog version - moves [Unreleased] to versioned section."""
from pathlib import Path
from datetime import date


def update_changelog_version(changelog_path: Path, version: str) -> bool:
    """
    Update changelog by moving [Unreleased] content to a new version section.
    
    Returns True if successful, False otherwise.
    """
    if not changelog_path.exists():
        return False
    
    content = changelog_path.read_text()
    
    # Check if [Unreleased] section exists
    if "## [Unreleased]" not in content:
        return False
    
    # Get today's date
    today = date.today().strftime("%Y-%m-%d")
    
    # Find the [Unreleased] section and its content
    import re
    
    # Pattern to match [Unreleased] section until the next ## heading or end of file
    unreleased_pattern = r'(## \[Unreleased\].*?)(?=\n## |\Z)'
    match = re.search(unreleased_pattern, content, re.DOTALL)
    
    if not match:
        return False
    
    old_unreleased = match.group(1)
    
    # Create new version section with the OLD [Unreleased] content
    new_version = old_unreleased.replace(
        "## [Unreleased]",
        f"## [{version}] - {today}"
    )
    
    # Create fresh empty [Unreleased] section
    empty_unreleased = """## [Unreleased]

### Added

### Changed

### Fixed

### Removed"""
    
    # Replace old [Unreleased] with new empty + version with content
    updated_content = content.replace(
        old_unreleased,
        f"{empty_unreleased}\n\n{new_version}"
    )
    
    changelog_path.write_text(updated_content)
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: update_version.py <version>", file=sys.stderr)
        sys.exit(1)
    
    changelog = Path("CHANGELOG.md")
    version = sys.argv[1]
    
    if update_changelog_version(changelog, version):
        print(f"Updated CHANGELOG.md with version {version}", file=sys.stderr)
    else:
        print("Failed to update changelog", file=sys.stderr)
        sys.exit(1)