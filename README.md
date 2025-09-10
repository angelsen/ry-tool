# ry

A command augmentation framework that wraps and enhances existing CLI tools without breaking their native behavior.

## Features

- **Command Augmentation**: Enhance existing CLI tools with validation, safety checks, and workflows
- **Clean Architecture**: Modular design with single-responsibility components  
- **Type-Safe Processing**: Recursive template processing with proper type dispatch
- **Token-Based Safety**: Time-limited tokens for dangerous operations
- **Library System**: Reusable command definitions with metadata
- **Direct Execution**: No shell escaping for safety

## Installation

```bash
pip install -e .
```

This installs the `ry` command globally.

## Quick Start

```bash
# List available libraries
ry --list

# Get help for a library
ry git --ry-help

# Execute augmented command
ry git commit -m "feat: new feature"

# Show execution plan (dry run)
ry --ry-run git commit -m "test"
```

## Production Libraries

- **git** - Enhanced git workflow with review tokens and commit validation
- **uv** - Python package management with automated version workflows
- **changelog** - Simple changelog management following Keep a Changelog
- **ry-lib** - Library development and management tools
- **site-builder** - Static documentation site generator

## Library System

### Example: Git Enhancement

```yaml
version: "2.0"
name: git
type: augmentation
target: /usr/bin/git

commands:
  commit:
    flags:
      m/message: string
    augment:
      before:
        - python: |
            # Validation logic
      relay: native
```

### Token-Based Safety

Critical operations require preview and token verification:

```bash
# Preview changes
ry git diff --staged  # → Generates REVIEW_TOKEN

# Execute with token
REVIEW_TOKEN=xxx ry git commit -m "message"
```

## Project Structure

```
ry-tool/
├── src/ry_tool/         # Core implementation
├── docs/
│   ├── libraries/       # Production libraries
│   └── ARCHITECTURE.md  # Technical documentation
├── examples/            # Example libraries
└── CLAUDE.md           # AI assistant guidance
```

## Development

```bash
# Run linter
ruff check src/ry_tool/ --fix

# Build distribution
uv build

# Create a new library
ry ry-lib create <name> <type>

# Validate libraries
ry ry-lib validate --all
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - Technical details and design
- [Library Development](docs/libraries/ry-lib/README.md) - Creating custom libraries
- [Examples](examples/README.md) - Working examples
- [Style Guide](docs/libraries/OUTPUT_STYLE_GUIDE.md) - Output formatting standards

## License

MIT