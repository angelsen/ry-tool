# ry Vision

## Philosophy: Augment, Don't Replace

ry enhances existing tools with safety, automation, and transparency - without replacing them.

### Core Principle

**Use real commands, get better behavior:**
- `git commit` → adds validation and review workflow
- `uv version --bump` → adds changelog update, atomic commit/tag
- `uv publish` → adds safety checks and token validation

Users learn the actual tools, ry just makes them safer and more powerful.

### What We Have Now

**Core Engine:**
- Pure YAML → Shell command generation
- Multi-word pattern matching (`"version --bump"`)
- Template variables with defaults (`{{args.0|default}}`)
- Dynamic YAML tags (`!env`, `!shell`, `!if`, etc.)
- Capture directive for command output
- Pipeline, parallel, and conditional execution
- Argument consumption for intuitive parameter handling

**Augmentation Libraries:**
- `docs/libraries/git/` - Git with review tokens and commit validation
- `docs/libraries/uv/` - uv with atomic version management
- `docs/libraries/changelog/` - Changelog automation
- `docs/libraries/ry-lib/` - Library version management
- `docs/libraries/site-builder/` - Static site generation

### How It Works Today

```bash
# Augmented commands via guard wrappers
git commit -m "feat: new feature"     # Enhanced by ry
uv version --bump minor               # Enhanced by ry
uv build && uv publish                # Enhanced by ry

# Direct ry libraries for new functionality
ry ry-lib check                       # Check library versions
ry changelog init                     # Initialize changelog
ry site-builder generate              # Build static site
```

## The Augmentation Pattern

### Guard Wrappers Enable Transparent Enhancement
```bash
# ~/.local/bin/guards/git (in PATH before /usr/bin)
#!/bin/bash
eval "$(ry git "$@")"  # Augments git commands

# When user types: git commit -m "message"
# 1. Shell finds ~/.local/bin/guards/git first
# 2. ry processes libraries/git/git.yaml
# 3. Enhanced workflow executes
# 4. Eventually calls /usr/bin/git
```

### Two Types of Libraries

**1. Augmentation Libraries** - Enhance existing tools
- Match real command patterns
- Add safety checks and automation
- Fall through to original tool
- Examples: git, uv, docker, npm

**2. Utility Libraries** - Provide new functionality
- Don't map to existing tools
- Offer new capabilities
- Examples: changelog, ry-lib, site-builder

## Next Phase: Registry & Distribution

### Central Registry
```bash
ry --install git                      # Install from registry
ry --install git@1.2.0               # Specific version
ry --list                            # Show installed
ry --update git                      # Update to latest
ry --search "docker"                 # Find libraries
```

### GitHub-Based Distribution
```yaml
# https://angelsen.github.io/ry-tool/registry.json
{
  "libraries": {
    "git": {
      "version": "1.2.0",
      "files": ["git.yaml", "lib/token.py", "meta.yaml"],
      "author": "angelsen"
    }
  }
}
```

### Library Installation
```
~/.local/share/ry/libraries/
├── git/                    # From registry
│   ├── git.yaml
│   ├── meta.yaml
│   └── lib/
├── docker/                 # Community library
│   ├── docker.yaml
│   └── lib/
```

## Design Principles

1. **Augment real commands** - Enhance existing tools, don't replace them
2. **Transparent logic** - YAML + scripts, always readable
3. **Safe by default** - Add review tokens, validation, atomic operations
4. **Version everything** - Pin libraries for reproducibility
5. **Local first** - Libraries download to local filesystem
6. **Override friendly** - Local libraries override downloaded ones
7. **Zero magic** - Always see what commands will run
8. **Exit codes for CI** - Machine-readable results for automation

## Why This Matters

Traditional CLI tools are black boxes with scattered safety:
- `git commit` - No validation
- `npm publish` - Easy to accidentally publish
- `docker push` - No safety checks

With ry augmentation:
- `git commit` - Requires review, validates format
- `uv publish` - Requires build token, checks tags
- `docker push` - Can add registry validation

## The Augmentation Advantage

**Tool Documentation Still Works**
- Users read official `uv` docs
- Commands work as documented
- ry adds safety without changing interface

**Progressive Enhancement**
- Start with: `/usr/bin/git commit -m "msg"`
- Enhance to: `git commit -m "msg"` (with validation)
- Escape to: `/usr/bin/git commit -m "msg"` (if needed)

**CI/CD Ready**
```bash
# Pre-commit hook
ry ry-lib check | sh          # Exit 0/1 for CI

# GitHub Actions  
- run: uv version --bump minor # Augmented with ry
- run: uv build                # Generates BUILD_TOKEN
- run: uv publish              # Validates before publishing
```

## End Goal

**Make every CLI tool safer without changing how people use them.**

Every command becomes augmentable through ry libraries that users can read, understand, customize, and share - while keeping the original tool's interface intact.
