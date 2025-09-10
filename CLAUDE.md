# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

ry is a command augmentation framework that wraps and enhances existing CLI tools without breaking their native behavior. It intercepts commands, adds validation, safety checks, and workflow enhancements, then relays to the original tool.

## Core Architecture

The codebase follows a clean modular architecture with single-responsibility components:

- **src/ry_tool/** - Core implementation
  - `app.py` - Main application orchestrator that wires together all modules
  - `parser.py` - Command line argument parsing and flag extraction
  - `loader.py` - Library YAML loading, validation, and discovery
  - `matcher.py` - Command matching to handlers
  - `executor.py` - Command execution engine with before/after hooks
  - `template.py` - Recursive template variable substitution
  - `context.py` - Execution context management
  - `installer.py` - Library installation and management
  - `utils.py` - Shared utilities and base classes
  - `_cli.py` - CLI framework with decorators

## Library System

Libraries are YAML files defining command augmentations, located in:
- `docs/libraries/` - Production libraries with support modules
- `examples/` - Example libraries for reference
- `~/.local/share/ry/libraries/` - User-installed libraries

Each library follows this structure:
```
library-name/
├── library-name.yaml  # Main definition (v2.0 format)
├── meta.yaml         # Version and metadata
├── README.md         # Documentation
└── lib/             # Python support modules
```

## Key Design Patterns

1. **Command Augmentation**: Libraries define `before`, `relay`, and `after` hooks
2. **Token-Based Safety**: Critical operations require time-limited review tokens
3. **Direct Subprocess Execution**: No shell escaping for safety
4. **Type Dispatch**: Recursive processing with proper type handling
5. **Environment Enrichment**: Libraries get RY_* environment variables and PYTHONPATH

## Development Commands

```bash
# Install package in editable mode
pip install -e .

# Run linter and auto-fix issues
ruff check src/ry_tool/ --fix

# Build distribution
uv build

# Test installation
python -m ry_tool --version

# List available libraries
ry --list

# Show execution plan (dry run)
ry --ry-run <command>

# Install a library
ry --install <library>

# Library development
ry ry-lib create <name> <type>
ry ry-lib validate <name>
ry ry-lib registry build
```

## Important Implementation Notes

- Always use full paths (e.g., `/usr/bin/git`) to prevent command recursion
- Libraries can import from their `lib/` directory via PYTHONPATH
- Template processing supports nested structures and environment variables
- The matcher supports both exact commands and wildcard patterns
- Relay can be "native" (pass to target), "none" (no relay), or custom command
- Augmentation libraries use `relay: native` not environment variable patterns
- The correct environment variable for target is `RY_TARGET` (not RY_TOOL)

## Project Structure

- `src/ry_tool/` - Core implementation (v2.0 library format)
- `docs/libraries/` - Production libraries
- `docs/ARCHITECTURE.md` - Technical architecture documentation
- `examples/` - Example libraries
- `_archive/` - Deprecated v1 code (not used)
- The command is installed as `ry`