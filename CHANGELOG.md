# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed
- **BREAKING**: Removed all `--dev-*` commands in favor of `ry-lib` library
  - `--dev-new` → `ry ry-lib init`
  - `--dev-check` → `ry ry-lib validate`
  - `--dev-registry` → `ry ry-lib registry`
  - `--dev-publish` → `ry ry-lib publish`
- Deleted `developer.py` module - all functionality now in `ry-lib` library

### Added

### Changed

### Fixed

### Removed

## [0.3.1] - 2025-09-09

### Added
- Centralized configuration system (`src/ry_tool/config.py`)
- Custom exception hierarchy (`src/ry_tool/exceptions.py`) 
- Unified base64 encoding method in base executor
- Local library installation support in package manager
- `ry-lib` library for library management (replaced ry-dev)
- Style enforcement system via `/enforce-ry-style` command
- Claude Code agents and commands for style checking
- Tool invocation safety patterns (prevent recursion)
- `changelog check` command for pre-commit hooks
- `changelog validate` command for CI/CD
- Comprehensive documentation in STYLE_GUIDE.md
- Workspace support for uv library with --package flags
- Hook snippet patterns (--hook-snippet) for git integration

### Changed
- All executors now use shared base64 encoding pipeline
- Registry operations unified with fallback to local
- Loader tags now raise exceptions instead of silent failures
- Template processor raises exceptions instead of sys.exit
- Renamed `ry-dev` to `ry-lib` for clarity
- `changelog update` renamed to `changelog bump`
- All libraries now use `/usr/bin/tool` for safety
- Augmentation libraries use `{{env.RY_TOOL|/usr/bin/tool}}` pattern
- All output now consistently goes to stderr
- Updated all documentation to reflect current state (not aspirational)
- ry-lib uses --hook-snippet instead of install-hooks
- uv library has strict fail-early checks

### Fixed
- YAML quoting issues in library files
- Normalizer script path execution bug
- Interactive command handling in guard wrappers
- Tool invocation recursion risks in helper scripts
- Missing stderr redirects in all libraries
- Unicode symbols replaced with text prefixes
- All meta.yaml files now have proper structure
- Git library args.rest vs args.all distinction
- All library CHANGELOGs now have [Unreleased] sections

## [0.3.0] - 2025-09-07

### Added
- Complete package management system (`--install`, `--update`, `--uninstall`, `--list`, `--search`)
- Developer tools (now removed in favor of ry-lib library)
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
