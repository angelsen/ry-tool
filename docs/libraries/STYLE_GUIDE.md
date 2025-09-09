# ry Library Style Guide

## Core Philosophy
**Pattern matcher routes → Workflow decides**

The `match` block is for routing to the right workflow based on command patterns. The actual logic lives in the workflow steps where it's visible and debuggable.

## Library Types

### Augmentation Libraries
Enhance existing commands without changing their interface:
- Examples: `git`, `uv`, `docker`, `npm`
- Use `{{env.RY_TOOL|/usr/bin/tool}}` pattern
- Default case should pass through: `default: - shell: "{{env.RY_TOOL|/usr/bin/tool}} {{args.all}}"`
- Only augment existing commands, never add new ones

### Utility Libraries  
Provide new functionality that doesn't map to existing tools:
- Examples: `changelog`, `ry-lib`, `site-builder`
- Default case should show help text
- Can define any commands needed

## File Structure

```yaml
# library-name.yaml - One-line description
# Usage: ry library-name <command> [args...]  # Note: no path needed

match:
  "command --flag":    # Multi-word patterns for specific cases
    - steps...
  
  command:             # Single word patterns for general cases
    - steps...
  
  default:             # Fallback - pass through OR help text
    - shell: |
        echo "Usage: ry library-name <command>" >&2
        echo "Commands:" >&2
        echo "  command1  - Description" >&2
```

### Meta.yaml Structure
```yaml
name: library-name
version: 0.1.0
description: One-line description of the library
author: Your Name
dependencies:  # Optional
  other-library: ">=0.1.0"
features:      # Optional, for documentation
  - Feature one
  - Feature two
commands:      # List of commands provided
  - init
  - build
usage: |       # Examples for users
  # Initialize project
  ry library-name init
```

## Pattern Matching Rules

1. **Longest Match First**: ry automatically sorts patterns by length
   ```yaml
   match:
     "version --bump":  # Matches before "version"
     "version --":      # Matches any --flag
     version:           # Fallback for just "version"
   ```

2. **No Wildcards Needed**: Patterns match prefixes
   ```yaml
   "version --bump":  # Matches: version --bump patch/minor/major
   ```

3. **Let Shell Decide**: Don't over-pattern, use shell logic
   ```yaml
   version:
     - shell: |
         if [ $# -gt 1 ]; then
           # User provided version number
           echo "Setting version to {{args.1}}"
         else
           # Just showing version
           uv version
         fi
   ```

## Step Types

### Shell Steps
```yaml
# Simple command
- shell: echo "Hello"

# Multi-line with proper indentation
- shell: |
    if [ -f "file.txt" ]; then
      echo "File exists"
    fi

# With capture
- shell: uv version --output-format json
  capture: VERSION_INFO
```

### Python Steps
```yaml
# Simple expression
- python: print("Hello")

# Multi-line with imports
- python: |
    import json
    import os
    data = json.loads(os.environ['VERSION_INFO'])
    print(data['version'])
  capture: VERSION

# Access library files
- python: |
    import sys
    import os
    from pathlib import Path
    lib_path = Path(os.environ['RY_LIBRARY_DIR']) / 'lib'
    sys.path.insert(0, str(lib_path))
    from my_module import my_function
```

### Script Steps (future)
```yaml
# Run Python script from library directory
- script: lib/build.py
```

## Templates

### Arguments
```yaml
{{args.0}}         # First argument (fails if missing)
{{args.1|}}        # Second argument (empty if missing)
{{args.all}}       # All arguments space-separated
{{args.rest|}}     # All except first (with fallback)
```

### Environment
```yaml
{{env.USER}}       # Environment variable
{{env.TOKEN|}}     # With empty fallback
```

### Best Practices
- Use `|` for optional values to prevent failures
- Put complex defaults after the pipe: `{{args.1|default-value}}`
- Templates work in any string context

## Variable Capture

```yaml
# Capture output for next steps
- shell: git branch --show-current
  capture: CURRENT_BRANCH

# Use captured variable
- shell: echo "On branch: $CURRENT_BRANCH"
```

## Error Handling

### Exit Early Pattern
```yaml
- shell: |
    if [ ! -f "required.txt" ]; then
      echo "ERROR: required.txt not found" >&2
      echo "  Run: ry tool init" >&2
      exit 1
    fi
```

### Python Validation
```yaml
- python: |
    import sys
    if not "{{args.1|}}":
      print("ERROR: Missing argument", file=sys.stderr)
      print("Usage: ry tool <arg>", file=sys.stderr)
      sys.exit(1)
```

## Library Conventions

### 1. CRITICAL: Use Environment Variables for Augmented Commands
For augmentation libraries, **always use environment variables with fallback** to allow bypass:

```yaml
# CORRECT - for augmentation libraries (git, uv, etc.)
- shell: "{{env.RY_GIT|/usr/bin/git}} status"
- shell: "{{env.RY_UV|/usr/bin/uv}} version"
- python: subprocess.run(["{{env.RY_GIT|/usr/bin/git}}", "add", "file.py"])

# WRONG - hardcoded paths don't allow bypass
- shell: /usr/bin/git status
- shell: git status  # Can cause infinite recursion
```

This pattern:
- Allows users to set `RY_GIT=/usr/bin/git` to bypass augmentation
- Falls back to `/usr/bin/git` if not set
- Prevents infinite recursion when users have wrapper scripts

For non-augmented tools, use absolute paths directly:
```yaml
# For tools we don't augment
- shell: /usr/bin/python3 script.py
- shell: /usr/bin/cat file.txt
```

### 2. Git Operations
- Check clean working directory before version changes
- Generate review tokens for commits
- Validate commit message format

### 3. Version Management
- Use JSON output format when available
- Package-aware tagging: `${PACKAGE_NAME}-v${VERSION}`
- Update CHANGELOG.md automatically
- Sync dependencies after version changes

### 4. User Feedback - ALWAYS to stderr
```yaml
# Shell - always redirect to stderr with >&2
echo "SUCCESS: Task completed" >&2
echo "ERROR: Description" >&2
echo "WARNING: Description" >&2
echo "INFO: Starting build process" >&2

# Python - always use file=sys.stderr
print("SUCCESS: Task completed", file=sys.stderr)
print("ERROR: Description", file=sys.stderr)
print("WARNING: Description", file=sys.stderr)
print("INFO: Starting build process", file=sys.stderr)

# Errors should include actionable next steps
echo "ERROR: No CHANGELOG.md found" >&2
echo "  Run: ry changelog init" >&2

# Success messages should be concise
echo "SUCCESS: Bumped version to 1.2.0" >&2
```

### 5. Path References
```yaml
# Use $RY_LIBRARY_DIR for library files
- shell: python $RY_LIBRARY_DIR/lib/script.py

# In Python, construct paths properly
- python: |
    from pathlib import Path
    import os
    lib_dir = Path(os.environ['RY_LIBRARY_DIR'])
    script = lib_dir / 'lib' / 'script.py'
```

## Common Patterns

### Pass-through Default
```yaml
default:
  - shell: /usr/bin/tool {{args.all}}
```

### Help Text Default
```yaml
default:
  - shell: |
      echo "Commands:" >&2
      echo "  init    - Initialize project" >&2
      echo "  build   - Build project" >&2
```

### Pre-flight Checks
```yaml
build:
  # Check prerequisites
  - shell: |
      if [ ! -f "package.json" ]; then
        echo "ERROR: No package.json found" >&2
        exit 1
      fi
  
  # Run build
  - shell: npm run build
```

### Conditional Git Operations
```yaml
# Only commit if version actually changed
- shell: |
    OLD=$(get_old_version)
    NEW=$(get_new_version)
    
    if [ "$OLD" = "$NEW" ]; then
      echo "No version change"
      exit 0
    fi
    
    # Version changed, do git operations
    git add -A
    git commit -m "bump: $OLD → $NEW"
```

## Testing Patterns

When developing libraries:
```bash
# Test pattern matching
ry library.yaml command --flag

# See generated commands without execution
ry library.yaml command | cat

# Test with environment variables
ENV_VAR=value ry library.yaml command
```

## Anti-patterns to Avoid

❌ **Over-patterning**
```yaml
# Bad: Too many specific patterns
match:
  "build --dev":
  "build --prod":
  "build --staging":
  "build --test":
```

✅ **Better: Let shell handle variations**
```yaml
match:
  build:
    - shell: npm run build {{args.rest|}}
```

❌ **Complex logic in patterns**
```yaml
# Bad: Trying to handle everything in match
match:
  "version 1.*":
  "version 2.*":
```

✅ **Better: Simple routing, complex logic in steps**
```yaml
match:
  version:
    - shell: |
        case "{{args.1|}}" in
          1.*) handle_v1 ;;
          2.*) handle_v2 ;;
        esac
```

❌ **Forgetting error messages**
```yaml
# Bad: Silent failure
- shell: test -f file.txt || exit 1
```

✅ **Better: Informative errors**
```yaml
- shell: |
    if [ ! -f file.txt ]; then
      echo "ERROR: file.txt not found" >&2
      echo "  Create it first with: touch file.txt" >&2
      exit 1
    fi
```

❌ **Missing stderr redirect**
```yaml
# Bad: Success/error messages to stdout
print("SUCCESS: Done")
echo "ERROR: Failed"
```

✅ **Better: All feedback to stderr**
```yaml
print("SUCCESS: Done", file=sys.stderr)
echo "ERROR: Failed" >&2
```

## Library File Organization

```
libraries/
├── library-name/
│   ├── library-name.yaml  # Main entry point
│   ├── meta.yaml          # Metadata (optional)
│   └── lib/               # Python modules
│       ├── __init__.py
│       └── helper.py
```

## Prefix Convention

Use consistent prefixes for all output to stderr:
- `SUCCESS:` - Operation completed successfully
- `ERROR:` - Fatal error, operation failed
- `WARNING:` - Non-fatal issue, operation continues
- `INFO:` - General information or progress
- `DEBUG:` - Detailed diagnostic information (when verbose)

Avoid Unicode symbols (✓, ✗, ✅, ❌) for better terminal compatibility.

## Summary

The key to good ry libraries:
1. **Simple patterns** - Just route to workflows
2. **Clear errors** - Always tell users what to do next
3. **Shell logic** - Use shell for conditionals and flow control
4. **Visible operations** - Show what's happening with consistent prefixes
5. **Clean templates** - Use `|` for optional values
6. **Atomic operations** - Group related changes (like git add + commit)
7. **Consistent output** - Use PREFIX: style for all stderr messages