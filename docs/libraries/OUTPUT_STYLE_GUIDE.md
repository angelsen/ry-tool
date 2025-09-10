# Ry-Tool Output Style Guide

This guide defines consistent output patterns for all ry-tool libraries to ensure a predictable and user-friendly experience.

## Core Principles

1. **Be concise** - One line per instruction
2. **Show commands** - Always provide exact commands to run
3. **No redundancy** - Avoid repeating obvious information
4. **Progressive disclosure** - Basic info first, details with --verbose
5. **Consistent formatting** - Follow the patterns below

## Output Streams

- **stdout**: Data output only (actual results, JSON, YAML, file contents)
- **stderr**: All user messages (status, errors, hints, progress, confirmations)

## Message Prefixes

Use these UTF-8 symbols consistently:

```
✅ Success/completion
❌ Error/failure  
📦 Building/packaging/processing
📝 Info/next steps
💡 Tips (sparingly, only when helpful)
⚠️  Warning (potential issues)
🔑 Security/authentication related
📋 Review/preview required
🌐 Network/server related
ℹ️  Neutral information
🔄 In progress/updating
```

## Standard Output Patterns

### Success Messages

```python
# Simple success
print("✅ Action completed", file=sys.stderr)

# Success with next step
print("✅ Action completed", file=sys.stderr)
print("📝 Next: ry-next [command]", file=sys.stderr)

# Success with multiple next steps
print("✅ Version bumped to 1.2.0", file=sys.stderr)
print("📝 Next steps:", file=sys.stderr)
print("   1. ry-next ry-lib project sync", file=sys.stderr)
print("   2. ry-next site-builder build", file=sys.stderr)
print("   3. git add -A && git commit", file=sys.stderr)
```

### Error Messages

```python
# Simple error
print("❌ File not found", file=sys.stderr)
sys.exit(1)

# Error with remedy
print("❌ Project.yaml not found", file=sys.stderr)
print("   Run: ry-next ry-lib project init", file=sys.stderr)
sys.exit(1)

# Error with alternatives
print("❌ Working directory not clean", file=sys.stderr)
print("   Commit: git add -A && git commit", file=sys.stderr)
print("   Or stash: git stash", file=sys.stderr)
sys.exit(1)
```

### Token/Authentication

```python
# Token generation
print(f"📋 REVIEW_TOKEN={token}", file=sys.stderr)
print(f"   Expires in {expires} seconds", file=sys.stderr)
print(f"   Use: REVIEW_TOKEN={token} git commit -m 'message'", file=sys.stderr)

# Missing token
print("❌ Review required", file=sys.stderr)
print("   Get token: git diff --staged --stat", file=sys.stderr)
print("   Use: REVIEW_TOKEN=<token> git commit -m 'message'", file=sys.stderr)
```

### Progress Indicators

```python
# Starting action
print(f"📦 Building {package}...", file=sys.stderr)

# Multi-step process
print("🔄 Step 1/3: Validating...", file=sys.stderr)
print("🔄 Step 2/3: Building...", file=sys.stderr)
print("🔄 Step 3/3: Packaging...", file=sys.stderr)
print("✅ Complete", file=sys.stderr)
```

## Command Help Format

### Library Help (--ry-help)
Generated from library YAML metadata (name, version, type, description, commands).

```yaml
library-name - Brief one-line description
Version: X.Y.Z
Type: augmentation|utility|library

Commands:
  command1        Action verb phrase (no period)
  command2        Action verb phrase
  command3        Action verb phrase

Common workflow:
  ry-next lib init           # Initialize project
  ry-next lib build          # Build artifacts
  ry-next lib publish        # Publish to registry
```

### Command-Specific Help
Defined in YAML under `commands.<name>.description` and flag descriptions.

```yaml
# In library.yaml:
commands:
  build:
    description: Generate static site from project.yaml
    flags:
      theme:
        description: Site theme to use
```

## Spacing and Formatting

### Indentation
- Use 3 spaces for indented continuation lines
- Use 2 spaces for numbered lists

```python
print("📝 Next steps:", file=sys.stderr)
print("  1. First step", file=sys.stderr)
print("  2. Second step", file=sys.stderr)
print("     With details", file=sys.stderr)  # 5 spaces for sub-items
```

### Line Wrapping
- Keep lines under 80 characters when possible
- Break at logical points (after operators, commas)

### Empty Lines
- No empty lines in output (keeps terminal compact)
- Use indentation to show hierarchy

## Special Cases

### File Staging (git add)
```python
print("📝 Files staged", file=sys.stderr)
print("   Review: git diff --staged --stat", file=sys.stderr)
print("   Commit: REVIEW_TOKEN=<token> git commit -m 'message'", file=sys.stderr)
```

### Version Bumping
```python
print(f"✅ Bumped {package}: {old} → {new}", file=sys.stderr)
print("📝 Next steps:", file=sys.stderr)
print("   1. ry-next ry-lib project sync", file=sys.stderr)
print("   2. ry-next site-builder build", file=sys.stderr)
```

### Build Operations
```python
print("📦 Building...", file=sys.stderr)
# ... build process ...
print("✅ Build complete", file=sys.stderr)
print("📝 Next: uv publish --dry-run", file=sys.stderr)
```

### Interactive Prompts
```python
# Use stderr for prompts
print("Continue? [y/N]: ", file=sys.stderr, end='')
response = input()  # stdin
```

## Anti-Patterns to Avoid

### ❌ Too Verbose
```python
# BAD - Too much detail
print("✅ Build complete (2 files)", file=sys.stderr)
print("   - dist/package-1.0.0.tar.gz (24.8KiB)", file=sys.stderr)
print("   - dist/package-1.0.0-py3-none-any.whl (30.4KiB)", file=sys.stderr)
print("   1. Test locally: pip install dist/*.whl", file=sys.stderr)
print("   2. Dry run: uv publish --dry-run", file=sys.stderr)
```

### ✅ Concise
```python
# GOOD - Just what's needed
print("✅ Build complete", file=sys.stderr)
print("📝 Next: uv publish --dry-run", file=sys.stderr)
```

### ❌ Redundant Information
```python
# BAD - States the obvious
print("✅ Successfully completed successfully", file=sys.stderr)
print("   The build has finished building", file=sys.stderr)
```

### ✅ Direct
```python
# GOOD - Clear and direct
print("✅ Build complete", file=sys.stderr)
```

### ❌ Inconsistent Prefixes
```python
# BAD - Mixed symbols
print(">> Building...", file=sys.stderr)
print("[OK] Built", file=sys.stderr)
print("==> Next steps:", file=sys.stderr)
```

### ✅ Consistent
```python
# GOOD - Consistent symbols
print("📦 Building...", file=sys.stderr)
print("✅ Built", file=sys.stderr)
print("📝 Next steps:", file=sys.stderr)
```

## Common Implementation Patterns

### In Library YAML (inline Python)
```yaml
execute:
  - python: |
      # Imports available: sys, os, subprocess, json, yaml, Path, ry_tool
      from pathlib import Path
      
      # Status to stderr
      print("📦 Processing...", file=sys.stderr)
      
      # Data to stdout (only for 'show' type commands)
      print(yaml.dump(data))
      
      # Error handling
      if error:
          print(f"❌ {error_msg}", file=sys.stderr)
          print(f"   Fix: {remedy}", file=sys.stderr)
          sys.exit(1)
      
      # Success with next steps
      print("✅ Complete", file=sys.stderr)
      print(f"📝 Next: ry-next {next_cmd}", file=sys.stderr)
```

### In Library Python Scripts (lib/*.py)
```python
#!/usr/bin/env python3
"""Module description."""

from pathlib import Path
from ry_tool.utils import LibraryBase

class MyHandler(LibraryBase):
    """Handle operations with consistent output."""
    
    def process(self, item: str) -> bool:
        """Process with proper output patterns."""
        # Progress
        self.info_message(f"📦 Processing {item}...")
        
        try:
            # ... do work ...
            
            # Success
            self.success_message("Complete")
            self.info_message(f"📝 Next: ry-next {next_cmd}")
            return True
            
        except Exception as e:
            # Error with remedy
            self.error_message(str(e))
            print(f"   Fix: {remedy}", file=sys.stderr)
            return False

# When called from YAML
def main_function(arg1, arg2):
    """Entry point from YAML execute block."""
    handler = MyHandler()
    return handler.process(arg1)
```

### Environment Variables
```yaml
# In YAML - use os.environ for shell vars
- python: |
    import os
    token = os.environ.get('REVIEW_TOKEN', '')  # From shell
    path = env.get('RY_LIBRARY_DIR')           # From ry-tool
```

## Implementation Checklist

When updating or creating a library:

- [ ] All user messages go to stderr
- [ ] Only data output goes to stdout
- [ ] Use consistent emoji prefixes
- [ ] Include exact commands in error messages
- [ ] Show next steps after success
- [ ] Keep messages concise (one line when possible)
- [ ] Use 3-space indentation for continuations
- [ ] Exit with proper codes (0 success, 1 failure)
- [ ] Import from ry_tool.utils for library scripts
- [ ] Use os.environ.get() for shell environment variables
- [ ] Use env.get() for ry-tool provided variables
- [ ] Test output in both success and failure cases
- [ ] Ensure --ry-help follows the format

## Examples by Library Type

### Augmentation Library (git, uv)
- Show tokens and exact usage
- Include relay information when relevant
- Guide through safety workflows

### Utility Library (changelog, ry-lib)
- Focus on workflow steps
- Show file paths being modified
- Provide next logical commands

### Service Library (site-builder)
- Show input/output locations
- Provide access URLs or paths
- Indicate processing status

## Testing Output

Before committing, test your output:

1. **Success path**: Does it show what succeeded and what to do next?
2. **Error path**: Does it explain what went wrong and how to fix it?
3. **Token flow**: Are tokens clearly shown with usage examples?
4. **Help text**: Is --ry-help concise and helpful?
5. **Verbosity**: Could any message be shorter while remaining clear?

## Version History

- v1.0 (2025-09-10): Initial style guide