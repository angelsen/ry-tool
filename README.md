# ry - YAML Command Orchestrator

**Augment, don't replace** - Enhance existing tools with YAML-defined workflows. Generate shell commands, never execute directly.

## Install

```bash
# Install ry
uv tool install ry-tool

# Install augmentation libraries
ry --install git       # Enhanced git workflows
ry --install uv        # Python package management
ry --install changelog # Changelog management
```

## Usage

```bash
# Use augmented commands (after installation)
git commit -m "feat: amazing"   # Enhanced with validation
uv version --bump minor         # Atomic version management

# Or use ry directly
ry workflow.yaml          # Generate commands
ry workflow.yaml | sh     # Execute
ry workflow.yaml test     # Pass arguments
```

## Core Concepts

**YAML defines logic** → **ry generates commands** → **shell executes**

### Templates

```yaml
steps:
  - shell: echo "Hello, {{args.0|World}}!"  # First arg or "World"
  - shell: echo "User: {{env.USER}}"        # Environment variable
```

### Pattern Matching

```yaml
match:
  test:
    - shell: pytest
  build:
    - shell: python -m build
  default:
    - shell: echo "Usage: ry task.yaml [test|build]"
```

### Multi-word Pattern Matching

```yaml
match:
  "version --bump":  # Matches: uv version --bump minor
    - shell: echo "Enhanced bump workflow"
  version:           # Matches: uv version
    - shell: echo "Regular version command"
```

### Dynamic YAML Tags

- `!env USER` - Environment variable
- `!shell date +%Y` - Command output
- `!if <condition>` - Conditional execution
- `!eval 2 + 2` - Python evaluation
- `!include other.yaml` - Include files
- `!exists /path` - Check file existence
- `!read file.txt` - Read file contents

### Structures

```yaml
# Sequential
steps:
  - shell: echo "Step 1"
  - python: print("Step 2")

# Piped together
pipeline:
  - shell: ls
  - shell: grep ".yaml"

# Conditional
if: !env CI
then:
  - shell: npm test
else:
  - shell: npm run dev
```

## Available Libraries

### git - Enhanced Git Workflows
```bash
# After installation: ry --install git
git add .                                      # Normal git command
git diff --stat --staged                       # Generates review token
REVIEW_TOKEN=xxx git commit -m "feat: new"     # Validated commit
git tag v1.0.0                                 # Auto-updates changelog
```
- Review token workflow prevents blind commits
- Conventional commit validation
- AI signature stripping
- Automatic changelog updates on tags

### uv - Python Package Management
```bash
# After installation: ry --install uv
uv version --bump minor    # Atomic: version + changelog + commit + tag
uv version 1.0.0          # Set specific version with same workflow
uv publish                # Requires proper git tag
```
- Clean git state validation
- Automatic CHANGELOG.md updates
- Package-aware tagging (e.g., `my-package-v1.0.0`)
- Atomic operations (no partial states)

### changelog - Keep a Changelog Format
```bash
# After installation: ry --install changelog
ry changelog init          # Create CHANGELOG.md template
ry changelog bump 1.0.0    # Move [Unreleased] to version section
ry changelog check         # Verify [Unreleased] has content (for hooks)
ry changelog validate      # Validate format (for CI/CD)
```

### ry-lib - Library Management
```bash
# After installation: ry --install ry-lib
ry ry-lib init my-lib      # Create new library from template
ry ry-lib validate         # Check all library YAML syntax
ry ry-lib check-versions   # Verify changed libraries have version bumps
ry ry-lib bump git patch   # Bump library version
ry ry-lib registry         # Update library registry
```

## How Augmentation Works

When you install a library with `ry --install git`, it:
1. Copies the library to `~/.local/share/ry/libraries/git/`
2. Creates a wrapper script at `~/.local/bin/git` (if guards enabled)
3. The wrapper intercepts git commands and enhances them via ry

You can always bypass augmentation:
- Use `/usr/bin/git` for the original command
- Set `RY_GIT=/usr/bin/git` environment variable
- Uninstall with `ry --uninstall git`

## Creating Your Own Libraries

```yaml
# my-deploy.yaml
match:
  staging:
    - shell: |
        echo "Deploying to staging..."
        kubectl apply -f k8s/staging/
  production:
    - shell: |
        if [ -z "$DEPLOY_TOKEN" ]; then
          echo "ERROR: Production requires DEPLOY_TOKEN" >&2
          exit 1
        fi
        kubectl apply -f k8s/production/
```

Use directly or install:
```bash
ry my-deploy.yaml staging              # Direct use
ry --install my-deploy.yaml            # Install as 'my-deploy'
my-deploy staging                      # Use after installation
```

## Philosophy

1. **Augment, Don't Replace** - Enhance existing tools, keep their interface
2. **Transparent** - All logic is readable YAML, no hidden behavior
3. **Composable** - YAML → shell commands → any executor
4. **Safe** - Never executes directly, only generates commands
5. **Escapable** - Always have a way to bypass augmentation
