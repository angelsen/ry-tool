# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Complete migration from ry-next to ry naming**
  - Renamed all internal references from ry-next back to ry
  - Updated all library YAML files and documentation
  - Fixed wrapper scripts in ~/.local/bin/guards/
  - Consolidated documentation structure
  - Removed redundant README files (README_PROJECT.md, docs/README_RYNEXT.md)
  - Added comprehensive ARCHITECTURE.md documentation
  - Added release-workflow command for automated releases
  - This completes the transition from experimental ry-next to production ry

## [1.2.1] - 2025-09-11

### Changed
- **OUTPUT_STYLE_GUIDE.md updated to v2.0** - ASCII-only prefixes for maximum compatibility
  - Replaced emoji prefixes (✅ ❌ 📦 etc.) with ASCII prefixes (SUCCESS: ERROR: BUILD: etc.)
  - Maintains all modern formatting improvements (indentation, remediation, next steps)
  - Better compatibility with SSH, logs, CI/CD systems, and all terminals
- **All production libraries updated to ASCII-only style**
  - changelog library: 13 violations fixed
  - ry-lib library: 54 violations fixed including templates
  - site-builder library: 8 violations fixed
  - git library: ~25 violations fixed
  - uv library: 44 violations fixed
  - Total: ~144 emoji/Unicode symbols replaced with ASCII prefixes
- **Enforcement tools updated**
  - ry-library-enforcer agent now enforces ASCII-only prefixes
  - enforce-ry-style command updated to check for v2.0 compliance

### Fixed
- **Critical bug: RY_TOOL environment variable doesn't exist**
  - Git library was using non-existent `{{env.RY_TOOL|/usr/bin/git}}` pattern
  - Correct environment variable is `RY_TARGET` (from context.target field)
  - Fixed git library to use `relay: native` for proper pass-through
  - Updated all documentation to reflect correct augmentation patterns
- **Augmentation library patterns corrected**
  - Augmentation libraries should use `relay: native` not env variable templates
  - Fixed enforcement tools to check for correct patterns

## [1.2.0] - 2025-09-10

### Added
- **OUTPUT_STYLE_GUIDE.md** - Comprehensive formatting guide for consistent library outputs
  - Standardized emoji prefixes for different message types
  - Clear stderr/stdout separation patterns
  - Consistent error messages with remediation steps
- **Template-based library creation** - New template system for ry-lib
  - `templates/utility.yaml` and `templates/augmentation.yaml` for quick scaffolding
  - Automatic template variable substitution
  - Improved library creation workflow
- **Enhanced documentation**
  - `CLAUDE.md` for Claude Code integration and guidance
  - `llms.txt` with complete workflow documentation for LLM context
  - Workflow examples in all library help outputs
- **Git workflow improvements**
  - Automatic changelog validation and update on tagging
  - Better staging feedback with Task agent hint for large changes
  - Enhanced token expiration messages

### Changed
- **All libraries updated to follow OUTPUT_STYLE_GUIDE.md**
  - Consistent use of emoji prefixes (✅ ❌ 📦 📝 ⚠️ 🔑 📋 ℹ️ 🔄 💡)
  - Proper stderr/stdout separation across all outputs
  - Standardized error messages with clear remediation steps
- **Improved error handling**
  - All error messages now include exact commands to fix issues
  - Better token verification feedback
  - More helpful validation messages
- **Library management enhancements**
  - Registry builder with improved validation
  - Version manager with better token flow
  - Create library using templates instead of hardcoded structure

### Fixed
- Changelog core now properly checks for unreleased content before tagging
- Git library validates changelog has changes before allowing tags
- All Python modules now properly output to stderr
- Token verification uses correct environment variable access

## [1.1.0] - 2025-09-10

### Added
- **Clean Python path architecture** - Automatic PYTHONPATH setup in executor
  - No more `sys.path.insert()` calls needed in libraries
  - Cross-library imports work seamlessly (e.g., uv can import from git's token_manager)
  - All library `lib/` directories automatically added to Python path
- **Site builder library** - Static documentation generator from project.yaml
  - Generates beautiful HTML documentation from project manifests
  - Supports minimal and terminal themes
  - Direct file:// URL for browser viewing (no server needed)
- **Project manifest management** in ry-lib
  - `ry-lib project init` - Create project.yaml with auto-detected metadata
  - `ry-lib project sync` - Update manifest from pyproject.toml
  - `ry-lib project validate` - Validate manifest structure
  - `ry-lib project show` - Display current manifest
- **Improved library structure patterns**
  - Direct `execute:` for simple commands
  - `handlers:` with `when:` conditions only for conditional logic
  - Removed unnecessary `handlers: - default:` nesting

### Changed
- **All libraries now use clean imports**
  - Direct imports: `from module import function`
  - No path manipulation: imports just work
  - Cleaner, more maintainable code
- **Environment variable handling**
  - Fixed `env.get()` vs `os.environ.get()` usage
  - Shell environment variables (like REVIEW_TOKEN) now properly accessible
  - Executor provides both `env` dict and preserves `os.environ`

### Fixed
- Site-builder command execution (was silently failing due to handler structure)
- Token verification in git and uv libraries (env.get → os.environ.get)
- Executor now displays captured stdout/stderr to user
- Library Python modules can import ry_tool.utils without setup

## [1.0.1] - 2025-09-10

### Fixed
- Fixed argument parsing for augmentation libraries to preserve exact user input
  - Numeric flags like `-10` are no longer incorrectly converted to `--10`
  - Commands like `git log --oneline -10` now work correctly through ry-next wrappers
  - Augmentation libraries now use raw unparsed arguments for relay to native tools
- Fixed uv library's publish check to use `uv version --output-format json` instead of parsing dist filenames
  - More reliable package name and version detection
  - Properly handles packages with hyphens in names

## [1.0.0] - 2025-09-10

### Changed
- **BREAKING**: Complete migration to ry-next as primary tool
  - Removed old 'ry' command entry point
  - Archived old ry_tool implementation
  - src/ry_next/ renamed to src/ry_tool/ (to match package name)
- Restructured project for cleaner organization
  - Libraries moved to docs/libraries/ for badge builder
  - Examples cleaned up and consolidated
  - Old documentation archived to _archive/
- Updated all wrappers and paths to new structure

## [0.4.0] - 2025-09-10

### Added
- **ry-next**: Complete rewrite with clean architecture
  - Modular design with single-responsibility components
  - No backward compatibility - clean API design
  - Type-safe recursive template processing
  - Direct subprocess execution without shell escaping
  - Context factory pattern for centralized logic
  - Error handling decorators and command builder utilities
- Shared utilities base class (`utils.py`) for library modules
  - `LibraryBase` for common library operations
  - `CommandBuilder` for subprocess execution
  - `FileManager` for YAML/JSON operations
  - `VersionManager` for semantic versioning
- 4 production-ready libraries in v2.0 format:
  - `git`: Enhanced workflow with review tokens and commit validation
  - `uv`: Python package management with automated workflows
  - `changelog`: Simple changelog management
  - `ry-lib`: Library development and management tools
- Token-based safety system for dangerous operations
- Library installation and management (`--install`, `--uninstall`)
- Environment variable setup for library execution
- 3 clean example libraries demonstrating core patterns

### Changed
- **BREAKING**: All library modules now require direct class instantiation
  - No convenience wrapper functions
  - `process_recursive()` replaces `process_dict/process_list`
  - `CommandBuilder().run_git()` instead of `run_git()`
- Libraries moved to `docs_next/libraries/` for v2.0 format
- Examples reorganized under `docs_next/examples/`
- Documentation consolidated under `docs_next/ry-next/`

### Fixed
- Fixed `git add` command missing `relay: native` directive
- Dataclass boilerplate using `field(default_factory)`
- Template processing with proper type dispatch

### Removed
- **BREAKING**: All backward compatibility code removed
- Convenience wrapper functions in library modules
- Redundant documentation files (HANDOFF_RYNEXT.md, outdated examples)
- `process_dict()` and `process_list()` methods (use `process_recursive()`)

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
