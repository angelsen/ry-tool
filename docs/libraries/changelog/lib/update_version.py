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
    
    # Create new version section header
    new_section = f"## [{version}] - {today}"
    
    # Replace [Unreleased] with new [Unreleased] and version section
    # This keeps empty [Unreleased] at top and moves content to version
    updated_content = content.replace(
        "## [Unreleased]",
        f"""## [Unreleased]

### Added

### Changed

### Fixed

### Removed

{new_section}"""
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