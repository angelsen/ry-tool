---
description: Execute the complete release workflow with configurable stop points
argument-hint: [commit|changelog|version|push|publish|full]
allowed-tools: Read, Edit, MultiEdit, Bash, Task, TodoWrite
---

Execute the ry release workflow up to the specified stage for ${ARGUMENTS:-full}.

## Workflow Stages

1. **commit** - Stage and commit current changes
2. **changelog** - Update CHANGELOG.md with unreleased changes
3. **version** - Bump version (patch/minor/major)
4. **push** - Push to origin with tags
5. **publish** - Build and publish to PyPI
6. **full** - Complete workflow (all stages)

## Stage Details

### Stage 1: Commit
- Check for uncommitted changes
- Stage all changes (`git add -A`)
- Get review token (`git diff --staged`)
- Commit with descriptive message

### Stage 2: Changelog
- Verify CHANGELOG.md has [Unreleased] content
- If empty, prompt for changes to add
- Validate changelog format

### Stage 3: Version
- Determine bump type (patch/minor/major)
- Preview version bump (`ry uv version --bump <type> --dry-run`)
- Execute bump with token
- Auto-commits and tags

### Stage 4: Push
- Push commits to origin
- Push tags to origin
- Verify push succeeded

### Stage 5: Publish
- Clean dist directory
- Build distribution (`ry uv build`)
- Verify with dry-run (`ry uv publish --dry-run`)
- Publish to PyPI with token

## Execution Plan

Based on ARGUMENTS, execute stages:
- **commit**: Stage 1 only
- **changelog**: Stages 1-2
- **version**: Stages 1-3
- **push**: Stages 1-4
- **publish** or **full**: Stages 1-5

## Pre-flight Checks

Before starting:
1. Verify we're in a ry project (pyproject.toml exists)
2. Check git repository status
3. Verify ry command is available
4. Check for CHANGELOG.md existence

## Workflow Execution

For each stage up to the stop point:

### Commit Stage
```bash
# Check git status
git status

# If changes exist:
git add -A
git diff --staged  # Get REVIEW_TOKEN
REVIEW_TOKEN=xxx git commit -m "commit message"
```

### Changelog Stage
```bash
# Check for unreleased content
ry changelog validate

# If no unreleased content:
# Prompt user to add changes to CHANGELOG.md
# Then re-validate
```

### Version Stage
```bash
# Determine bump type based on CHANGELOG content
# - Breaking changes → major
# - New features → minor  
# - Bug fixes → patch

# Preview bump
ry uv version --bump <type> --dry-run

# Execute with token
BUMP_TOKEN=xxx ry uv version --bump <type>
```

### Push Stage
```bash
git push origin main
git push origin --tags
```

### Publish Stage
```bash
# Clean and build
rm -rf dist/*
ry uv build

# Verify and publish
ry uv publish --dry-run
PUBLISH_TOKEN=xxx ry uv publish
```

## Error Handling

At each stage, if an error occurs:
1. Report the error clearly
2. Show exact command to fix
3. Stop workflow execution
4. Save progress state for resume

## Success Reporting

After completion:
- Show summary of completed stages
- Display new version number
- Provide links (PyPI, GitHub release)
- Show next recommended actions

## Implementation Notes

1. Use TodoWrite to track stage progress
2. Check each command's exit code
3. Capture tokens for reuse if needed
4. Show clear status at each stage
5. Allow resuming from last successful stage

Start by checking pre-flight conditions, then execute stages up to ${ARGUMENTS:-full}.

ARGUMENTS: ${ARGUMENTS}
