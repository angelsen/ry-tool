# ry Vision

## Current State: Command Platform with Libraries

ry has evolved from a simple command generator to a platform with a growing library ecosystem.

### What We Have Now

**Core Engine:**
- Pure YAML → Shell command generation
- Multi-word pattern matching (`"version --bump"`)
- Template variables with defaults (`{{args.0|default}}`)
- Dynamic YAML tags (`!env`, `!shell`, `!if`, etc.)
- Capture directive for command output
- Pipeline, parallel, and conditional execution

**Bundled Libraries:**
- `libraries/git/` - Enhanced git workflows with review tokens
- `libraries/uv/` - Package-aware version management
- `libraries/changelog/` - Keep a Changelog format support

### How It Works Today

```bash
# Using bundled libraries
ry libraries/git/git.yaml commit "feat: new feature"
ry libraries/uv/uv.yaml version --bump minor
ry libraries/changelog/changelog.yaml init

# Custom workflows
ry my-workflow.yaml deploy production
```

## Next Phase: Community Libraries

### Package Management
```bash
ry --install github.com/ry-libs/docker    # Download library
ry --list                                 # Show installed libraries
ry --update git                           # Update library
```

### Library Discovery
```yaml
# .ry/libraries.yaml
libraries:
  git:
    source: github.com/ry-libs/git
    version: v1.2.0
  docker:
    source: github.com/user/docker-workflows
    version: main
```

### Library Structure
```
~/.ry/libraries/
├── git@v1.2.0/
│   ├── git.yaml
│   ├── meta.yaml
│   └── lib/
├── docker@main/
│   ├── docker.yaml
│   └── lib/
```

## Design Principles

1. **Libraries are just YAML + scripts** - No compiled code, always readable
2. **Version everything** - Pin to specific versions for reproducibility
3. **Local first** - Libraries download to local filesystem
4. **Override friendly** - Local libraries override downloaded ones
5. **Zero magic** - You can always see what commands will run

## Why This Matters

Traditional CLI tools are black boxes. You run `git commit` and hope it does the right thing. With ry libraries:

- **See the logic** - Open the YAML to understand the workflow
- **Modify locally** - Fork and customize for your needs
- **Share improvements** - Contribute back to the community
- **Compose workflows** - Chain libraries together

## End Goal

Transform how we think about command-line tools:

**Before:** Binary executables with hidden logic
**After:** Transparent YAML workflows with community contributions

Every complex CLI tool can become a simple ry library that users can read, understand, modify, and share.
