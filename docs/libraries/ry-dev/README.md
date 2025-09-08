# ry-dev

Version management and development tools for ry libraries.

## Installation

```bash
ry --install ry-dev
```

## Usage

```bash
ry ry-dev list              # List all library versions
ry ry-dev bump git patch    # Bump library version
ry ry-dev check-versions    # Check if versions need bumping
ry ry-dev install-hooks     # Install git pre-commit hook
```

## Commands

- `list` - Show versions of all libraries
- `bump <lib> <type>` - Bump library version (patch/minor/major)
- `check-versions` - Verify changed libraries have version bumps
- `install-hooks` - Install git hooks for version enforcement
- `test` - Verify library is working
- `version` - Display ry-dev version
