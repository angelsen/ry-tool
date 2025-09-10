# ry Architecture Guide

## Overview

ry is a command augmentation framework that intercepts CLI commands, adds validation, safety checks, and workflow enhancements, then relays to the original tool. It achieves this without breaking native tool behavior through a clean, modular architecture.

## Core Architecture

```
src/ry_tool/
├── app.py       # Main application orchestrator
├── parser.py    # Command line argument parsing  
├── loader.py    # Library YAML loading and validation
├── matcher.py   # Command matching to handlers
├── executor.py  # Command execution engine
├── template.py  # Template variable substitution
├── context.py   # Execution context management
├── installer.py # Library installation and management
├── utils.py     # Shared utilities and base classes
└── _cli.py      # CLI framework with decorators
```

### Component Responsibilities

#### app.py - Application Orchestrator
- Wires together all modules
- Handles global flags (--list, --install, --ry-run, etc.)
- Routes commands to appropriate libraries
- Manages execution flow

#### parser.py - Argument Parser
- Parses command-line arguments without external dependencies
- Extracts flags, arguments, positionals
- Preserves exact user input for augmentation libraries
- Handles special cases like numeric flags (-10)

#### loader.py - Library Loader
- Discovers libraries from multiple paths
- Validates YAML structure
- Loads library definitions and metadata
- Manages library search paths (workspace, user, cached)

#### matcher.py - Command Matcher
- Matches user commands to library handlers
- Supports exact and wildcard patterns
- Handles conditional handlers with `when` clauses
- Builds execution steps from matched handlers

#### executor.py - Execution Engine
- Executes shell, Python, subprocess, and Ruby code
- Manages execution context and environment
- Handles relay to native commands
- Supports interactive and background execution

#### template.py - Template Processor
- Recursive template variable substitution
- Type-safe processing with dispatch
- Supports nested structures
- Handles environment variables and defaults

#### context.py - Execution Context
- Single source of truth for execution state
- Manages flags, arguments, environment
- Tracks captured variables
- Provides context to templates and code

## Library System

### Library Format v2.0

Libraries are YAML files defining command augmentations:

```yaml
version: "2.0"
name: library-name
type: augmentation|utility
target: /usr/bin/tool  # For augmentation libraries

commands:
  command-name:
    description: Command description
    flags:
      flag-name: string|bool|int
    arguments:
      arg-name: required|optional
    
    # For utilities
    execute:
      - shell: echo "command"
      - python: |
          print("Python code")
    
    # For augmentation
    augment:
      before: [...]
      relay: native
      after: [...]
```

### Library Structure

```
library-name/
├── library-name.yaml  # Main definition
├── meta.yaml         # Version and metadata
├── README.md         # Documentation
└── lib/             # Python support modules
```

### Library Types

1. **Augmentation Libraries**: Enhance existing tools
   - Must have `target` field
   - Use `relay: native` for pass-through
   - Cannot add new commands

2. **Utility Libraries**: Provide new functionality
   - No target field
   - Define custom commands
   - Should have default help text

## Execution Flow

1. **Command Reception**: User runs `ry git commit -m "msg"`
2. **Parsing**: Parser extracts library (git), command (commit), flags, args
3. **Loading**: Loader finds and loads git library
4. **Matching**: Matcher finds commit handler in library
5. **Context Creation**: Context populated with all execution variables
6. **Template Processing**: Templates resolved with context
7. **Execution**: Steps executed in sequence (before, relay, after)
8. **Result**: Output returned to user

## Environment Variables

### Set by ry

- `RY_LIBRARY_NAME` - Current library name
- `RY_LIBRARY_VERSION` - Library version
- `RY_LIBRARY_DIR` - Path to library directory
- `RY_LIBRARY_PATH` - Full path to library YAML
- `RY_TARGET` - Target binary for augmentation libraries
- `RY_<CONTEXT_FIELD>` - All context fields prefixed with RY_

### Python Path Setup

- Library `lib/` directories added to PYTHONPATH
- Cross-library imports supported
- `ry_tool` module available in Python blocks

## Safety Features

### Token System
Time-limited tokens for dangerous operations:
- Generated on preview (e.g., `git diff --staged`)
- Required for execution (e.g., `REVIEW_TOKEN=xxx git commit`)
- Stored in temp files with expiration

### Direct Execution
- No shell interpretation of arguments
- Direct subprocess calls prevent injection
- Full paths prevent command recursion

### Type Safety
- Recursive processing with type dispatch
- Proper handling of all data types
- No string concatenation for commands

## Template System

### Variable Access
- `{{flags.name}}` - Access flags
- `{{arguments.name}}` - Access arguments
- `{{env.VAR}}` - Environment variables
- `{{captured.name}}` - Captured variables
- `{{positionals}}` - Positional arguments

### Special Variables
- `{{args.all}}` - All arguments as string
- `{{args.rest}}` - Remaining arguments
- `{{args.original}}` - Original command line

### Defaults
- `{{env.VAR|default}}` - With default value
- `{{flags.name|}}` - Empty default

## Development Patterns

### Creating Libraries

```python
from pathlib import Path
from ry_tool.utils import LibraryBase

class MyHandler(LibraryBase):
    def process(self):
        # Implementation
```

### Error Handling

All errors follow OUTPUT_STYLE_GUIDE.md:
```python
print("ERROR: Description", file=sys.stderr)
print("   Fix: exact command", file=sys.stderr)
sys.exit(1)
```

### Testing

```bash
# Dry run to see execution plan
ry --ry-run command

# Check library validity
ry ry-lib validate library-name

# Run linter
ruff check src/ry_tool/ --fix
```

## Performance Considerations

- Libraries cached after first load
- Template processing is lazy
- Python imports cached via sys.path
- Minimal dependencies (only PyYAML)

## Future Enhancements

- Plugin system for custom executors
- Remote library repositories
- Parallel execution support
- Interactive mode improvements