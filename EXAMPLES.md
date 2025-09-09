# ry Examples

## Philosophy: Augment Real Commands

ry enhances existing tools without changing their interface. Users type normal commands, get better behavior.

## Package Development Workflow

### Traditional Workflow (Error-Prone)
```bash
# Easy to forget steps, make mistakes
vim pyproject.toml           # Manually edit version
vim CHANGELOG.md             # Manually update changelog
git add -A                   
git commit -m "bump"         # Poor commit message
git tag v1.2.0              # Might forget
git push && git push --tags  # Separate pushes
uv build
uv publish                   # Might publish wrong build
```

### With ry Augmentation (Safe & Atomic)
```bash
# Atomic version bump with changelog update
uv version --bump minor
# ry: ✓ Validates clean git state
# ry: ✓ Updates version to 1.2.0
# ry: ✓ Updates CHANGELOG.md from [Unreleased]
# ry: ✓ Commits "chore: bump version to 1.2.0"
# ry: ✓ Tags v1.2.0
# Output: Bumped to 1.2.0

# Build with safety
uv build
# ry: ✓ Verifies version is tagged
# ry: ✓ Builds distribution
# ry: ✓ Generates BUILD_TOKEN=a7f3c2
# Output: Built example-1.2.0.tar.gz
#         Ready to publish with: BUILD_TOKEN=a7f3c2 uv publish

# Publish with validation
BUILD_TOKEN=a7f3c2 uv publish
# ry: ✓ Validates BUILD_TOKEN matches dist/
# ry: ✓ Confirms version tagged
# ry: ✓ Checks not already published
# ry: ✓ Publishes to PyPI
# Output: Published example 1.2.0
```

## Git Workflow

### Traditional Git (No Safety)
```bash
git add .
git commit -m "fixed stuff"     # Bad message
git push                        # Straight to main
```

### With ry Augmentation (Enforced Best Practices)
```bash
# Review before commit
git diff --staged
# Shows diff...
# ry: Generated REVIEW_TOKEN=8b2f1a (expires in 300s)

# Commit with validation
REVIEW_TOKEN=8b2f1a git commit -m "fix: resolve null pointer in auth handler"
# ry: ✓ Valid review token
# ry: ✓ Conventional commit format
# ry: ✓ No AI signatures detected
# Output: [main 5a7c2f1] fix: resolve null pointer in auth handler

# Protected push
git push
# ry: ✗ Direct push to main blocked
#       Create a feature branch:
#       git checkout -b fix/auth-handler
#       git push -u origin fix/auth-handler
```

## Workspace/Monorepo Workflow

### Managing Multiple Packages
```bash
# Bump specific package in workspace
uv version --bump patch --package backend
# ry: ✓ Updates backend/pyproject.toml to 2.1.3
# ry: ✓ Updates backend/CHANGELOG.md
# ry: ✓ Commits "chore: bump backend to 2.1.3"
# ry: ✓ Tags backend-v2.1.3

# Build specific package
uv build --package backend
# ry: ✓ Verifies backend-v2.1.3 tag exists
# ry: ✓ Generates BUILD_TOKEN specific to backend

# Publish specific package
BUILD_TOKEN=xxx uv publish --package backend
# ry: ✓ Validates token for backend package
# ry: ✓ Publishes backend 2.1.3
```

## Library Development

### Developing ry Libraries
```bash
# Check all library versions
ry ry-lib check-versions
# ✓ git: 0.1.1 (unchanged)
# ✗ uv: 0.1.0 (modified - needs version bump)
# ✓ changelog: 0.1.0 (unchanged)
# ERROR: uv library modified without version bump
# Exit code: 1

# Bump library version
ry ry-lib bump uv patch
# ✓ Updated docs/libraries/uv/meta.yaml to 0.1.1
# ✓ Updated docs/libraries/uv/CHANGELOG.md

# Update and publish registry
ry ry-lib registry
# ✓ Registry updated with 5 libraries
# ✓ File: docs/registry.json

ry ry-lib publish
# ✓ Committed "chore: update library registry"
# ✓ Pushed to origin
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup ry
        run: |
          pip install ry-tool
          ry --install git
          ry --install uv
      
      - name: Build
        run: uv build  # Augmented by ry
        
      - name: Test
        run: uv run pytest
        
      - name: Publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: |
          # ry augmentation validates everything
          BUILD_TOKEN=$(cat .build-token)
          BUILD_TOKEN=$BUILD_TOKEN uv publish
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check library versions (for ry development)
if [ -d "docs/libraries" ]; then
    ry ry-lib check-versions || {
        echo "ERROR: Library changed without version bump"
        echo "Run: ry ry-lib bump <library> patch"
        exit 1
    }
fi

# Check changelog has content
ry changelog check || {
    echo "ERROR: No changes documented in [Unreleased] section"
    exit 1
}
```

## Docker Workflow (Planned)

### Enhanced Docker Commands
```bash
# Build with validation
docker build -t myapp:latest .
# ry: ✓ Scanning Dockerfile for security issues
# ry: ✓ Checking base image vulnerabilities
# ry: ✓ Building image
# ry: ✓ Generated IMAGE_HASH=3f8a9c2

# Push with safety
IMAGE_HASH=3f8a9c2 docker push myapp:latest
# ry: ✓ Validated IMAGE_HASH matches built image
# ry: ✓ Confirmed registry credentials
# ry: ✓ Pushed myapp:latest
```

## NPM Workflow (Planned)

### Safe NPM Publishing
```bash
# Version bump
npm version minor
# ry: ✓ Clean git check
# ry: ✓ Updated package.json to 2.3.0
# ry: ✓ Updated CHANGELOG.md
# ry: ✓ Committed and tagged v2.3.0

# Publish with protection
npm publish
# ry: ✓ Version tag exists
# ry: ✓ Not already published
# ry: ✓ Running prepublish tests
# ry: ✓ Published to npm
```

## Custom Workflows

### Organization-Specific Augmentation
```yaml
# ~/.local/share/ry/libraries/deploy/deploy.yaml
match:
  "staging":
    - shell: |
        echo "🚀 Deploying to staging..."
        # Run tests
        ry ry-lib check | sh || exit 1
        # Build
        docker build -t app:staging .
        # Deploy
        kubectl apply -f k8s/staging/
        
  "production":
    - shell: |
        # Require approval token
        if [ -z "$DEPLOY_TOKEN" ]; then
          echo "ERROR: Production deploy requires DEPLOY_TOKEN"
          echo "Get approval at: https://deploy.company.com"
          exit 1
        fi
        # Deploy with zero-downtime
        kubectl set image deployment/app app=app:$VERSION
        kubectl rollout status deployment/app
```

Usage:
```bash
ry deploy staging           # Deploy to staging
DEPLOY_TOKEN=xxx ry deploy production  # Deploy to production
```

## Key Patterns

1. **Tokens for Safety** - REVIEW_TOKEN, BUILD_TOKEN, DEPLOY_TOKEN
2. **Atomic Operations** - Version+Changelog+Commit+Tag together  
3. **Exit Codes for CI** - Machine-readable success/failure
4. **Progressive Enhancement** - Can always bypass with /usr/bin/tool
5. **Real Commands** - Users type what they know, get better behavior

## Installation

```bash
# Install ry
pip install ry-tool

# Install augmentation libraries
ry --install git          # Git enhancements
ry --install uv           # Python package enhancements
ry --install changelog    # Changelog management
ry --install ry-lib       # Library development tools

# Setup guard wrappers (optional, for transparent augmentation)
ry --setup-guards git uv

# Now just use normal commands
git commit -m "feat: amazing"  # Augmented!
uv version --bump minor        # Augmented!
```

## The Power of Transparency

Every augmentation is just YAML you can read and modify:

```bash
# See what git commit actually does
cat ~/.local/share/ry/libraries/git/git.yaml

# Customize for your team
ry ry-lib init my-git              # Create from template
vim docs/libraries/my-git/my-git.yaml  # Add your rules
ry docs/libraries/my-git/my-git.yaml commit -m "custom workflow"
```

---

**Remember: ry doesn't replace tools, it makes them better.**