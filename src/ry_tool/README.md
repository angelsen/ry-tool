# ry - YAML Command Orchestrator

A pure command generator that transforms YAML configurations into shell commands.

## Philosophy

- **Generate, don't execute** - Output commands for inspection and piping
- **Simple and composable** - Each component does one thing well
- **Universal execution** - All languages use `-c` with proper escaping
- **Templates where needed** - `{{var|default}}` syntax that doesn't conflict

## Architecture

```
YAML → Loader → Generator → Normalizer → Executor → Commands
        ↓         ↓           ↓            ↓
     (tags)   (structure)  (canonical)  (compile)
```

### Components

- **loader.py** - YAML parsing with dynamic tags (!env, !shell, !if)
- **generator.py** - Orchestrates transformation pipeline
- **normalizer.py** - Converts various YAML formats to canonical form
- **template.py** - Substitutes `{{var|default}}` patterns
- **pipeline.py** - Simple state holder for execution context
- **executors/** - Language-specific command generation

## Usage

```bash
# Generate commands
ry config.yaml

# Execute commands
ry config.yaml | sh

# Pass arguments
ry config.yaml arg1 arg2 | sh

# Save commands
ry config.yaml > script.sh
```

## YAML Structures

### Sequential Steps
```yaml
steps:
  - shell: echo "Starting..."
  - python: print("Processing...")
  - shell: echo "Done"
```

### Pipeline (connected with pipes)
```yaml
pipeline:
  - shell: ls
  - python: |
      import sys
      for line in sys.stdin:
          print(line.upper())
```

### Parallel Execution
```yaml
parallel:
  - python: print("Task 1")
  - python: print("Task 2")
  - shell: echo "Task 3"
```

### Pattern Matching
```yaml
match:
  test:
    - shell: pytest
  build:
    - shell: python -m build
  default:
    - shell: echo "Usage: ry config.yaml [test|build]"
```

## Templates

Use `{{var|default}}` syntax:
- `{{args.0}}` - First argument (required)
- `{{args.1|default}}` - Second argument with default
- `{{env.USER}}` - Environment variable
- `{{args.all}}` - All arguments joined

## Adding Executors

Create `executors/newlang.py`:
```python
import shlex
from .base import Executor

class NewLangExecutor(Executor):
    name = "newlang"
    aliases = ("nl",)
    
    def compile(self, script, config=None):
        return f"newlang -e {shlex.quote(script)}"
```

Register in `executors/__init__.py`:
```python
from .newlang import NewLangExecutor
registry.register(NewLangExecutor())
```

## Design Principles

1. **No mixed concerns** - Each file has single responsibility
2. **Clean interfaces** - Executors just compile scripts
3. **Predictable behavior** - No magic, explicit is better
4. **Extensible** - Adding languages is ~10 lines of code