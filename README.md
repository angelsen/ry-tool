# ry - YAML Command Orchestrator

**CI/CD for humans** - Transform YAML into shell commands. No execution, just generation.

## Install

```bash
uv tool install ry-tool
```

## Usage

```bash
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

## Bundled Libraries

ry includes powerful libraries for common tasks:

### git - Enhanced Git Workflows
```bash
ry libraries/git/git.yaml add .
ry libraries/git/git.yaml commit "feat: add new feature"
```
- Review tokens ensure you review changes before committing
- Automatic commit message validation
- Branch protection for main/master

### uv - Package-aware Version Management
```bash
ry libraries/uv/uv.yaml version --bump minor  # 0.1.0 → 0.2.0
ry libraries/uv/uv.yaml version 1.0.0         # Set specific version
```
- Automatic CHANGELOG.md updates
- Package-aware tagging (e.g., `my-package-v1.0.0`)
- Atomic git operations (commit + tag)
- Workspace support ready

### changelog - Keep a Changelog Format
```bash
ry libraries/changelog/changelog.yaml init          # Create CHANGELOG.md
ry libraries/changelog/changelog.yaml update 1.0.0  # Update version
```

## Examples

See `examples/` directory for complete workflows.

## Philosophy

1. **Transparent** - See exactly what will run
2. **Composable** - Pipe to any shell or tool
3. **Universal** - Works with any language via `-c`
4. **Simple** - YAML in, commands out
