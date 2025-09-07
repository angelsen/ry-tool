# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete package management system (`--install`, `--update`, `--uninstall`, `--list`, `--search`)
- Developer tools (`--dev-check`, `--dev-new`, `--dev-registry`, `--dev-publish`)
- `libraries/site-builder/` - Static site generator for GitHub Pages documentation
- ExecutionContext class for clean state management
- Custom CLI framework replacing typer dependency
- Library resolver with XDG directory support
- Automatic `$RY_LIBRARY_DIR` environment variable for libraries
- Copy buttons on all code blocks in generated documentation

### Changed
- Moved library detection from core.py to resolver.py (proper separation of concerns)
- Libraries now use `$RY_LIBRARY_DIR` instead of hardcoded paths
- Documentation site now shows "Libraries" (fixed typo from "Libraryies")

### Fixed
- Critical indentation bug in normalizer.py causing undefined variable errors
- Removed 60+ lines of dead code from normalizer.py
- All ruff linting issues resolved

### Removed
- Redundant `script:` step type (use shell with $RY_LIBRARY_DIR instead)
- typer dependency (replaced with custom lightweight CLI)

## [0.2.0] - 2025-09-07

### Added
- Multi-word pattern matching support in `match:` blocks for commands like `"version --bump"`
- `libraries/uv/` - Enhanced uv operations with automatic changelog updates and git integration
- `libraries/changelog/` - Simple changelog management following Keep a Changelog format
- `uv version --bump` workflow with atomic git operations (commit + tag)
- Pre-flight checks for `uv publish` to ensure version is tagged
- Pre-flight check for `uv version --bump` to ensure CHANGELOG.md exists
- Automatic changelog version updates when bumping versions

### Changed
- Enhanced `_handle_match()` in generator.py to support multi-word patterns
- Pattern matching now sorts by length (longest first) for proper precedence
- Template processor now properly handles empty defaults after pipe character

### Fixed
- Git wrapper recursion issue by using absolute paths (/usr/bin/git)
- Template variable processing for empty defaults ({{args.rest|}})
- Changelog template comment format to use `<!-- ... --->`

### Removed

<!-- 
When version is bumped, the [Unreleased] section will automatically 
become the new version section. Make sure to add your changes above!
--->
