---
description: Check and enforce ry library style guide conventions
argument-hint: [library-name|all]
allowed-tools: Read, Edit, MultiEdit, Grep, Glob, Task
---

Enforce ry library style conventions for ${ARGUMENTS:-all} libraries in docs/libraries/.

## Workflow

### Phase 1: Analysis
Identify which libraries to check:
- If specific library name provided: check only that library
- If "all" or no argument: check all libraries except STYLE_GUIDE.md

For each library, determine:
1. Library type (augmentation vs utility)
2. Current compliance level
3. Specific violations

### Phase 2: Validation

**Structure checks**:
- [ ] Library directory exists at `docs/libraries/<name>/`
- [ ] Main YAML file matches directory name: `<name>.yaml`
- [ ] Meta.yaml exists with required fields
- [ ] If lib/ directory exists, helper scripts are referenced

**Style checks**:
- [ ] All print() statements include `file=sys.stderr`
- [ ] All echo statements include `>&2`
- [ ] No Unicode symbols (✅, ❌, ✓, ✗)
- [ ] Consistent PREFIX: format (SUCCESS:, ERROR:, WARNING:, INFO:)
- [ ] Shell commands with colons are properly quoted (e.g., `- shell: 'echo "ERROR: Failed"'`)

**Pattern checks for augmentation libraries (git, uv)**:
- [ ] Uses `{{env.RY_TOOL|/usr/bin/tool}}` pattern in YAML
- [ ] Has pass-through default case
- [ ] No new commands added (only augments existing)

**Pattern checks for utility libraries (changelog, ry-lib, site-builder)**:
- [ ] Has help text in default case
- [ ] Commands in meta.yaml match actual patterns
- [ ] Usage examples use correct format
- [ ] YAML uses `/usr/bin/tool` directly (NOT `{{env...}}`)

**Tool invocation safety (ALL libraries)**:
- [ ] No bare tool calls without absolute paths (`git` → `/usr/bin/git`)
- [ ] Helper scripts in lib/ always use `/usr/bin/tool`
- [ ] Only augmentation YAMLs use `{{env.RY_TOOL|...}}`

### Phase 3: Enforcement

Use the ry-library-enforcer agent to:
1. Fix output redirection issues
2. Replace Unicode symbols with PREFIX: style
3. Correct template patterns for augmented tools
4. Update meta.yaml if incomplete
5. Align help text with actual commands

### Phase 4: Verification

After fixes:
1. Verify YAML syntax is still valid
2. Check that all patterns still match correctly
3. Ensure no functionality was broken
4. Generate summary of changes

### Phase 5: Report

Provide clear summary:
- Libraries checked: X
- Clean libraries: Y
- Libraries fixed: Z
- Violations found and fixed:
  - Missing stderr redirects: N
  - Unicode symbols replaced: N
  - Pattern corrections: N

## Example Usage

```bash
# Check all libraries
/enforce-ry-style

# Check specific library
/enforce-ry-style git

# Check multiple libraries
/enforce-ry-style git uv changelog
```

## Success Criteria

A library passes style enforcement when:
1. All output goes to stderr
2. No Unicode symbols present
3. Correct template patterns used
4. Meta.yaml is complete and accurate
5. Commands are documented consistently

Start with Phase 1 analysis immediately.