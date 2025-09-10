# ry-next

Next generation command augmentation framework with clean architecture.

## What is ry-next?

ry-next is a command augmentation tool that wraps and enhances existing CLI tools without breaking their native behavior. It intercepts commands, adds validation, safety checks, and workflow enhancements, then relays to the original tool.

## Key Features

- **Clean Architecture**: Modular design with single-responsibility components
- **Command Augmentation**: Wrap existing tools with before/after hooks
- **Smart Relay**: Unmatched commands pass through to native tools
- **Type-Safe Processing**: Recursive template processing with type dispatch
- **Library System**: Reusable command definitions with metadata
- **No Shell Escaping**: Direct subprocess execution for safety

## Architecture

```
src/ry_next/
├── app.py       # Main application orchestrator
├── parser.py    # Command line argument parsing  
├── loader.py    # Library YAML loading and validation
├── matcher.py   # Command matching to handlers
├── executor.py  # Command execution engine
├── template.py  # Template variable substitution
├── context.py   # Execution context management
├── utils.py     # Shared utilities and base classes
└── _cli.py      # CLI framework with decorators
```

## Installation

```bash
pip install -e .
```

This installs the `ry-next` command globally.

## Usage

### Basic Commands

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

### Library Management

```bash
# Install a library to user directory
ry-next --install git

# Uninstall a library
ry-next --uninstall git

# List installed libraries
ry-next --list --installed
```

## Library Format (v2.0)

Libraries are YAML files that define command augmentations:

```yaml
version: "2.0"
name: git
type: augmentation
target: /usr/bin/git
description: Enhanced git workflow

commands:
  commit:
    description: Commit with validation
    flags:
      m/message: string  # -m or --message
      amend: bool
    
    # Augmentation with relay
    augment:
      before:
        - python: |
            if not flags.get('m'):
                print("Error: Message required", file=sys.stderr)
                sys.exit(1)
      relay: native
      after:
        - shell: echo "Committed successfully" >&2
```

## Library Structure

```
docs_next/libraries/
├── git/
│   ├── git.yaml        # Main library definition
│   ├── meta.yaml       # Version and metadata
│   ├── README.md       # Documentation
│   └── lib/            # Python support modules
│       ├── token_manager.py
│       └── commit_validator.py
```

## Available Libraries

### Core Libraries

- **git** - Enhanced git workflow with review tokens
- **uv** - Python package management with version automation
- **changelog** - Changelog management following Keep a Changelog
- **ry-lib** - Library development and management tools

### Example Libraries

Check `examples_next/` for simple examples:
- `hello.yaml` - Basic utility command
- `deploy.yaml` - Deployment workflow example
- `gum-test.yaml` - Interactive input with gum

## Development

### Creating a New Library

```bash
# Use ry-lib to scaffold a new library
python docs_next/libraries/ry-lib/lib/create_library.py my-lib utility

# This creates:
# docs_next/libraries/my-lib/
#   ├── my-lib.yaml
#   ├── meta.yaml
#   ├── README.md
#   └── lib/
```

### Validating Libraries

```bash
# Validate a specific library
python docs_next/libraries/ry-lib/lib/validate_library.py my-lib

# Validate all libraries
python docs_next/libraries/ry-lib/lib/validate_library.py --all
```

## Clean API (No Backward Compatibility)

This is a clean break from the original ry-tool. Key changes:

1. **Direct Class Usage**: No convenience wrappers
   ```python
   # Instead of: create_library(name)
   creator = LibraryCreator()
   creator.create_library(name)
   ```

2. **Explicit Builders**: For subprocess operations
   ```python
   # Instead of: run_git('status')
   CommandBuilder().run_git('status')
   ```

3. **Recursive Processing**: Single method for all data types
   ```python
   # Instead of: process_list(data)
   processor.process_recursive(data)
   ```

## Environment Variables

When executing libraries, ry-next sets:

- `RY_LIBRARY_NAME` - Current library name
- `RY_LIBRARY_VERSION` - Library version from meta.yaml
- `RY_LIBRARY_DIR` - Path to library directory
- `RY_LIBRARY_PATH` - Full path to library YAML
- `PYTHONPATH` - Includes library's lib/ directory

## Safety Features

- **Full Paths**: Uses `/usr/bin/git` to prevent recursion
- **Token System**: Time-limited tokens for dangerous operations
- **Direct Execution**: No shell interpretation of arguments
- **Type Checking**: All components properly typed

## Testing

```bash
# Run linter
ruff check src/ry_next/ --fix

# Test basic functionality
python -m src.ry_next --version

# Test library loading
python -m src.ry_next --list
```

## License

MIT