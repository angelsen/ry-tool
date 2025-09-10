# ry-next Examples

These examples demonstrate the core features of ry-next with working, tested code.

## Examples

### 1. hello.yaml - Simple Utility
A basic utility library showing:
- Command with optional arguments
- Boolean and integer flags  
- Python execution blocks
- Multiple commands in one library

**Usage:**
```bash
ry-next hello greet Fredrik --excited
ry-next hello greet --times 3
ry-next hello goodbye
```

### 2. git-simple.yaml - Command Augmentation
Simple git enhancements demonstrating:
- Augmentation with `relay: native`
- Before/after hooks
- Flag validation in Python
- Conditional handlers with `when` clauses
- Pass-through to native git

**Usage:**
```bash
ry-next git-simple status
ry-next git-simple commit -m "feat: new feature"
ry-next git-simple push origin main  # Shows warning
```

### 3. dev-workflow.yaml - Development Automation
Development workflow commands showing:
- Complex Python subprocess execution
- Shell commands with template variables
- Optional arguments with defaults
- Multi-step workflows
- Environment setup

**Usage:**
```bash
ry-next dev setup
ry-next dev test --coverage
ry-next dev format src/
ry-next dev clean
```

## Key Patterns

### Command Structure
```yaml
commands:
  command-name:
    description: What it does
    arguments:
      arg1: required|optional
    flags:
      flag1: string|bool|int
    execute:  # For utilities
      - shell: echo "Hello"
    augment:  # For augmentation
      before: [...]
      relay: native
      after: [...]
```

### Conditional Handlers
```yaml
handlers:
  - when: condition
    execute: [...]
  - default:
    relay: native
```

### Template Variables
- `{{arguments.name}}` - Access arguments
- `{{flags.verbose}}` - Access flags
- `{{env.USER}}` - Access environment
- `{{captured.var}}` - Access captured variables

## Testing Examples

All examples can be tested directly:

```bash
# Test any example
ry-next examples/hello.yaml greet

# Show execution plan
ry-next --ry-run examples/git-simple.yaml commit -m test

# Get help
ry-next examples/dev-workflow.yaml --ry-help
```