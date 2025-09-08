# ry Library Style Guide

## Core Philosophy
**Pattern matcher routes → Workflow decides**

The `match` block is for routing to the right workflow based on command patterns. The actual logic lives in the workflow steps where it's visible and debuggable.

## File Structure

```yaml
# library-name.yaml - One-line description
# Usage: ry libraries/library-name/library-name.yaml <command> [args...]

match:
  "command --flag":    # Multi-word patterns for specific cases
    - steps...
  
  command:             # Single word patterns for general cases
    - steps...
  
  default:             # Fallback with help text
    - shell: |
        echo "Usage: ry library-name <command>" >&2
        echo "Commands:" >&2
        echo "  command1  - Description" >&2
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

### 1. CRITICAL: Use Absolute Paths for Commands
**Always use absolute paths** like `/usr/bin/git` or `/usr/bin/uv` when calling system commands.

```yaml
# WRONG - can cause infinite recursion if user has wrapper scripts
- shell: git status
- shell: uv version
- python: subprocess.run(["python", "script.py"])

# CORRECT - always use absolute paths
- shell: /usr/bin/git status  
- shell: /usr/bin/uv version
- python: subprocess.run(["/usr/bin/python3", "script.py"])
```

This prevents:
- Infinite recursion when users have wrapper scripts (like `~/bin/git` that calls `ry git`)
- Issues with wrappers that don't handle stdin properly (common with Python wrappers)

### 2. Git Operations
- Check clean working directory before version changes
- Generate review tokens for commits
- Validate commit message format

### 3. Version Management
- Use JSON output format when available
- Package-aware tagging: `${PACKAGE_NAME}-v${VERSION}`
- Update CHANGELOG.md automatically
- Sync dependencies after version changes

### 4. User Feedback
```yaml
# Success messages to stderr (consistent prefix style)
echo "SUCCESS: Task completed" >&2
echo "SUCCESS: Built project in 2.3s" >&2

# Errors with actionable next steps
echo "ERROR: Description" >&2
echo "  Run: ry tool fix" >&2

# Warnings for non-fatal issues
echo "WARNING: Description" >&2
echo "  This might cause issues" >&2

# Info messages for progress
echo "INFO: Starting build process" >&2
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

❌ **Using Unicode symbols**
```yaml
# Bad: Not portable across all terminals
echo "✓ Done" >&2
echo "✗ Failed" >&2
```

✅ **Better: Consistent prefix style**
```yaml
echo "SUCCESS: Done" >&2
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
- `FAIL:` - Validation or check failed (shorter alternative to ERROR)

## Summary

The key to good ry libraries:
1. **Simple patterns** - Just route to workflows
2. **Clear errors** - Always tell users what to do next
3. **Shell logic** - Use shell for conditionals and flow control
4. **Visible operations** - Show what's happening with consistent prefixes
5. **Clean templates** - Use `|` for optional values
6. **Atomic operations** - Group related changes (like git add + commit)
7. **Consistent output** - Use PREFIX: style for all stderr messages