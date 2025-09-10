# ry-next

A clean, modular command augmentation framework that enhances existing CLI tools without breaking their native behavior.

## Features

- **Command Augmentation**: Wrap and enhance existing CLI tools
- **Clean Architecture**: Modular design with single-responsibility components  
- **Type-Safe Processing**: Recursive template processing with type dispatch
- **Token-Based Safety**: Time-limited tokens for dangerous operations
- **Library System**: Reusable command definitions with metadata
- **No Shell Escaping**: Direct subprocess execution for safety

## Installation

```bash
pip install -e .
```

This installs the `ry-next` command globally.

## Quick Start

```bash
# List available libraries
ry-next --list

# Get help for a library
ry-next git --ry-help

# Execute augmented command
ry-next git commit -m "feat: new feature"

# Show execution plan (dry run)
ry-next --ry-run git commit -m "test"
```

## Production Libraries

- **git** - Enhanced git workflow with review tokens and commit validation
- **uv** - Python package management with automated version workflows
- **changelog** - Simple changelog management following Keep a Changelog
- **ry-lib** - Library development and management tools

## Documentation

- [Full Documentation](docs/README_RYNEXT.md)
- [Library Development](docs/libraries/ry-lib/README.md)
- [Examples](examples/README.md)

## Project Structure

```
ry-next/
├── src/ry_next/         # Core implementation
├── docs/
│   ├── libraries/       # Production libraries
│   └── README_RYNEXT.md # Full documentation
├── examples/            # Example libraries
└── _archive/            # Old ry-tool code (deprecated)
```

## Key Concepts

### Library Format (v2.0)

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
git diff --staged  # → Generates REVIEW_TOKEN

# Execute with token
REVIEW_TOKEN=xxx git commit -m "message"
```

## Development

See [docs/README_RYNEXT.md](docs/README_RYNEXT.md) for complete documentation.

## License

MIT