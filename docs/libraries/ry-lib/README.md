# ry-lib

Library version management for ry - handles versioning, changelog updates, and validation for ry libraries.

## Installation

```bash
ry --install ry-lib
```

## Usage

```bash
ry ry-lib list              # List all library versions
ry ry-lib bump git patch    # Bump library version
ry ry-lib check-versions    # Check if versions need bumping
ry ry-lib install-hooks     # Install git pre-commit hook
```

## Commands

- `list` - Show versions of all libraries
- `bump <lib> <type>` - Bump library version (patch/minor/major)
- `check-versions` - Verify changed libraries have version bumps
- `install-hooks` - Install git hooks for version enforcement
- `test` - Verify library is working
- `version` - Display ry-lib version
