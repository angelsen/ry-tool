# changelog

Simple changelog initialization and release management.

## Overview

A minimal utility for managing CHANGELOG.md files:
- Creates Keep a Changelog format
- Converts Unreleased to versioned releases
- No dependencies
- **Manual editing encouraged** - no add commands by design

## Installation

```bash
ry --install changelog
```

## Commands

### `init` - Create new CHANGELOG.md

```bash
# Basic initialization
ry changelog init

# With project name
ry changelog init --name "My Project"
```

Creates a standard CHANGELOG.md with an [Unreleased] section.

### `release` - Create versioned release

```bash
# Release with today's date
ry changelog release 1.0.0

# Release with specific date
ry changelog release 2.0.0 --date 2025-01-01
```

Converts the [Unreleased] section to a versioned release and creates a new [Unreleased] section.

### `validate` - Check format

```bash
ry changelog validate
```

Validates that CHANGELOG.md follows the expected format.

### `show` - Display changelog

```bash
# Show entire changelog
ry changelog show

# Show only unreleased changes
ry changelog show --unreleased

# Show latest version
ry changelog show --latest
```

## Workflow

```bash
# 1. Initialize once
ry changelog init

# 2. Edit CHANGELOG.md manually as you work
vim CHANGELOG.md
# Add your changes under [Unreleased] in appropriate sections:
# - Added, Changed, Deprecated, Removed, Fixed, Security

# 3. When ready to release
ry changelog release 1.0.0

# 4. Continue editing for next release
vim CHANGELOG.md

# 5. Release again
ry changelog release 1.1.0
```

## Philosophy

This library is intentionally minimal:
- **No add command** - Edit CHANGELOG.md directly
- **No git integration** - You control what goes in
- **No automation** - Conscious, manual changelog management
- **Just helpers** - Init and release, that's it

The changelog is for humans, so humans should write it.