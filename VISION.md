# ry Vision

## Current: Command Generator
YAML → Commands → Shell

## Future: Command Platform
YAML + Libraries → Commands → Shell

## Library System

```yaml
# .ry/libraries.yaml
libraries:
  git: github.com/ry-libs/git
  release: github.com/ry-libs/release
  docker: github.com/ry-libs/docker
```

```bash
ry --install git       # Download library
ry git status         # Use library
```

## Library Structure

```
library/
├── git/
│   ├── git.yaml      # Main workflow
│   └── lib/          # Helper scripts
│       ├── validate_commit.py
│       └── check_staged.sh
```

## Why Libraries?

- **Reusable** - Share workflows across projects
- **Composable** - Mix and match capabilities
- **Versioned** - Pin to specific versions
- **Community** - Anyone can contribute

## End Goal

Replace complex CLI tools with simple YAML + scripts that users can read, understand, and modify.