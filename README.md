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

## Examples

See `examples/` directory for complete workflows.

## Philosophy

1. **Transparent** - See exactly what will run
2. **Composable** - Pipe to any shell or tool
3. **Universal** - Works with any language via `-c`
4. **Simple** - YAML in, commands out