# ry-lib

Library development and management for ry-next.

## Overview

ry-lib is the foundational library for creating and managing other ry-next libraries. It provides tools for:
- Creating new libraries with proper structure
- Validating library configurations
- Managing library versions
- Building library registries
- Publishing libraries

## Installation

```bash
# Install to user directory
ry-next --install ry-lib

# Or use directly from docs_next/libraries
ry-next ry-lib --ry-help
```

## Commands

### `init` - Create a new library

```bash
# Create a utility library
ry-next ry-lib init my-lib

# Create an augmentation library
ry-next ry-lib init git-tools --type augmentation --target /usr/bin/git

# Create a hybrid library
ry-next ry-lib init dev-tools --type hybrid
```

### `validate` - Validate library structure

```bash
# Validate a specific library
ry-next ry-lib validate --library my-lib

# Validate all libraries
ry-next ry-lib validate --all

# Verbose validation
ry-next ry-lib validate --all --verbose
```

### `bump` - Update library version

```bash
# Patch version bump (0.1.0 -> 0.1.1)
ry-next ry-lib bump my-lib

# Minor version bump (0.1.0 -> 0.2.0)
ry-next ry-lib bump my-lib --type minor

# Major version bump (0.1.0 -> 1.0.0)
ry-next ry-lib bump my-lib --type major --message "Breaking changes"
```

### `list` - List libraries

```bash
# List all available libraries
ry-next ry-lib list

# List installed libraries
ry-next ry-lib list --installed

# Output as JSON
ry-next ry-lib list --json
```

### `check-versions` - Version checking for git hooks

```bash
# Check if changed libraries have version bumps
ry-next ry-lib check-versions

# Show git hook setup
ry-next ry-lib check-versions --hook
```

### `registry` - Generate library registry

```bash
# Generate registry.json
ry-next ry-lib registry

# Pretty print
ry-next ry-lib registry --pretty

# Custom output path
ry-next ry-lib registry --output /tmp/registry.json
```

### `publish` - Commit and push library changes

```bash
# Update registry and commit
ry-next ry-lib publish

# Custom commit message
ry-next ry-lib publish --message "feat: add new libraries"

# Also push to remote
ry-next ry-lib publish --push
```

## Library Structure

Libraries created with ry-lib follow this structure:

```
docs_next/libraries/my-lib/
├── my-lib.yaml      # Library definition (v2.0 format)
├── meta.yaml        # Library metadata
├── README.md        # Documentation
├── CHANGELOG.md     # Version history
└── lib/             # Helper scripts (optional)
    └── *.py         # Python modules
```

## Development

ry-lib uses helper scripts in the `lib/` directory to keep the YAML clean:
- `create_library.py` - Library creation logic
- `validate_library.py` - Validation logic
- `version_manager.py` - Version management
- `registry_builder.py` - Registry generation

## Architecture

ry-lib is designed to be:
- **Self-contained**: No external dependencies
- **Bootstrapping**: Can create itself and other libraries
- **Clean**: Logic separated into lib/ scripts
- **v2.0 native**: Built for ry-next, not ry-tool

## Examples

### Creating a Git augmentation library

```bash
# Create the library
ry-next ry-lib init git-extras --type augmentation --target /usr/bin/git

# Edit the generated YAML
vim docs_next/libraries/git-extras/git-extras.yaml

# Validate it
ry-next ry-lib validate --library git-extras

# Test it
ry-next git-extras --ry-help

# Install for regular use
ry-next --install git-extras
```

### Setting up git hooks

```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
ry-next ry-lib check-versions || exit 1
```

This ensures all library changes include version bumps.