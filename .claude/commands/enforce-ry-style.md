---
description: Check and enforce ry library OUTPUT_STYLE_GUIDE.md conventions (v2.0)
argument-hint: [library-name|all]
allowed-tools: Read, Edit, MultiEdit, Grep, Glob, Task
---

Enforce ry library style conventions per OUTPUT_STYLE_GUIDE.md v2.0 (ASCII prefixes) for ${ARGUMENTS:-all} libraries in docs/libraries/.

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

**Style checks (Per OUTPUT_STYLE_GUIDE.md v2.0)**:
- [ ] All user messages use ASCII prefixes (SUCCESS:, ERROR:, BUILD:, INFO:, etc.)
- [ ] All print() statements include `file=sys.stderr` (except data output)
- [ ] All echo statements include `>&2` (except data output) 
- [ ] NO emoji/Unicode symbols (✅, ❌, 📦, 📝, etc.) - ASCII only
- [ ] Error messages include remediation steps ("Run: command")
- [ ] Success messages include next steps where appropriate
- [ ] Shell commands with colons are properly quoted

**Pattern checks for augmentation libraries (git, uv)**:
- [ ] Has `target: /usr/bin/tool` in YAML header
- [ ] Uses `relay: native` for pass-through commands
- [ ] Has default case with `relay: native`
- [ ] No new commands added (only augments existing)

**Pattern checks for utility libraries (changelog, ry-lib, site-builder)**:
- [ ] Has help text in default case
- [ ] Commands in meta.yaml match actual patterns
- [ ] Usage examples use correct format
- [ ] YAML uses `/usr/bin/tool` directly (NOT `{{env...}}`)
- [ ] Has `workflows:` section with usage examples

**Tool invocation safety (ALL libraries)**:
- [ ] No bare tool calls without absolute paths (`git` → `/usr/bin/git`)
- [ ] Helper scripts in lib/ always use `/usr/bin/tool`
- [ ] Augmentation libraries use `relay: native` not env patterns

### Phase 3: Enforcement

Use the ry-library-enforcer agent to:
1. Replace emoji/Unicode with ASCII prefixes (✅ → SUCCESS:, ❌ → ERROR:, etc.)
2. Fix output redirection issues (add missing `file=sys.stderr` or `>&2`)
3. Add remediation steps to error messages
4. Add next steps to success messages where appropriate
5. Add `workflows:` section if missing
6. Correct template patterns for augmented tools
7. Update meta.yaml if incomplete
8. Align help text with actual commands

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
  - Emoji/Unicode replaced with ASCII: N
  - Missing stderr redirects: N
  - Error messages without remediation: N
  - Missing workflows sections: N
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
1. All user messages use ASCII prefixes (SUCCESS:, ERROR:, etc.)
2. All output properly directed (stderr for messages, stdout for data)
3. No emoji/Unicode symbols present (ASCII only)
4. Error messages include remediation steps
5. Success messages include next steps where relevant
6. Has `workflows:` section with usage examples
7. Correct template patterns used for library type
8. Meta.yaml is complete and accurate
9. Commands are documented consistently

Start with Phase 1 analysis immediately.