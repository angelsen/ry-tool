#!/bin/bash
# Create a new ry library with proper structure
set -e

lib_name="$1"
if [ -z "$lib_name" ]; then
    echo "ERROR: Library name required" >&2
    echo "  Usage: ry ry-lib init <library>" >&2
    exit 1
fi

# Validate library name (alphanumeric and hyphens only)
if ! echo "$lib_name" | grep -qE '^[a-z0-9-]+$'; then
    echo "ERROR: Library name must contain only lowercase letters, numbers, and hyphens" >&2
    exit 1
fi

lib_dir="docs/libraries/$lib_name"
if [ -d "$lib_dir" ]; then
    echo "ERROR: Library '$lib_name' already exists" >&2
    exit 1
fi

echo "📝 Creating new library: $lib_name"
mkdir -p "$lib_dir/lib"

# Create main YAML file
cat > "$lib_dir/${lib_name}.yaml" << EOF
# $lib_name library for ry
# Generated template - customize as needed

match:
  test:
    - shell: 'echo "SUCCESS: $lib_name library is working!"'
  
  version:
    - shell: 'echo "$lib_name version 0.1.0"'
  
  default:
    - shell: |
        echo "Usage: ry $lib_name <command>"
        echo "Commands:"
        echo "  test    - Run tests"
        echo "  version - Show version"
EOF

# Create meta.yaml
cat > "$lib_dir/meta.yaml" << EOF
name: $lib_name
version: "0.1.0"
description: "$lib_name library for ry"
author: "$(/usr/bin/git config user.name 2>/dev/null || echo 'ry-tool')"
EOF

# Create README.md
cat > "$lib_dir/README.md" << EOF
# $lib_name

$lib_name library for ry.

## Installation

\`\`\`bash
ry --install $lib_name
\`\`\`

## Usage

\`\`\`bash
ry $lib_name test        # Run tests
ry $lib_name version     # Show version
\`\`\`

## Development

To test locally:
\`\`\`bash
ry docs/libraries/$lib_name/${lib_name}.yaml test
\`\`\`

## Commands

- \`test\` - Verify library is working
- \`version\` - Display library version
EOF

# Create CHANGELOG using changelog library if available
if command -v ry >/dev/null 2>&1 && ry --list 2>/dev/null | grep -q changelog; then
    echo "Creating CHANGELOG.md..."
    cat > "$lib_dir/CHANGELOG.md" << EOF
# Changelog - $lib_name

All notable changes to the $lib_name library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - $(date +%Y-%m-%d)

### Added
- Initial release of $lib_name library
- Basic command structure with test and version commands
EOF
else
    # Fallback if changelog library not available
    cat > "$lib_dir/CHANGELOG.md" << EOF
# Changelog - $lib_name

## [0.1.0] - $(date +%Y-%m-%d)
- Initial release
EOF
fi

echo "SUCCESS: Created library at $lib_dir" >&2
echo "" >&2
echo "Next steps:" >&2
echo "  1. Edit: $lib_dir/${lib_name}.yaml"
echo "  2. Test: ry $lib_dir/${lib_name}.yaml test | sh"
echo "  3. Update registry: ry ry-lib registry | sh"
echo "  4. Install locally: ry --install $lib_name"