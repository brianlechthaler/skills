---
name: shrink-code
description: >-
  Analyze a codebase and reduce lines of code without reducing functionality —
  deduplicate logic, remove dead code, collapse verbose patterns, and simplify
  over-abstractions. Use when the user asks to shrink, simplify, minimize, or
  reduce LOC; remove redundancy; or make the codebase smaller while preserving
  behavior.
---

# Shrink Code

Reduce **lines of code (LOC)** by removing redundancy and unnecessary complexity while **preserving every observable behavior**. Smaller codebases are easier to read, test, and maintain — but only when nothing breaks.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| User asks to shrink, simplify, deduplicate, or reduce LOC | Rewriting for a new architecture or framework |
| Redundant helpers, dead code, copy-paste logic | Removing features or changing public API without approval |
| Verbose patterns that have idiomatic shorter forms | Obfuscation or code golf that hurts readability |
| Over-abstracted layers with no reuse benefit | Generated, vendored, or third-party code |
| Post-feature cleanup to tighten a module | Repo has no tests and user has not accepted manual verification |

When unsure and the target area has obvious duplication or dead paths, default to applying this skill incrementally.

## Core Rule

**Shrink, never amputate.** Every behavior, edge case, error path, and public contract that must survive simplification is tagged **critical** before any code is deleted.

## Workflow

Copy and track:

```
Shrink-code progress:
- [ ] Baseline: LOC and scope recorded
- [ ] Behavior inventory tagged (critical vs optional)
- [ ] Candidates identified (dead code, duplication, verbosity)
- [ ] Changes applied in small batches
- [ ] Tests and linters pass after each batch
- [ ] Final LOC and savings reported
```

### Step 1 — Baseline and scope

1. Confirm **scope** with the user when ambiguous: whole repo, directory, or specific files.
2. Record baseline metrics for the scope:

```bash
# Example — adapt to project conventions
find src -name '*.py' | xargs wc -l
cloc src --json
git diff --stat origin/main  # when shrinking a branch
```

3. Note entry points, public APIs, and test coverage for the scoped area.

### Step 2 — Tag critical behavior

Before deleting anything, list **critical** behaviors as one-line assertions:

```markdown
Critical behavior (must remain true after edits):
- [ ] POST /users returns 201 with same JSON shape on valid input
- [ ] Invalid email returns 400 with error code `invalid_email`
- [ ] Retry logic runs at most 3 times on 5xx
```

Derive items from tests, docs, types, and call sites. If behavior is untested and unclear, add or run tests **before** shrinking — do not guess.

**Optional** candidates (safe to remove when verified unused): unreachable branches, duplicate helpers, unused imports, one-line wrappers, commented-out code, debug-only paths.

### Step 3 — Find shrink candidates

Scan in priority order:

| Priority | Pattern | Typical action |
|----------|---------|----------------|
| 1 | **Dead code** | Unused functions, unreachable branches, stale feature flags | Delete |
| 2 | **Duplication** | Copy-paste logic, parallel helpers | Extract shared function or inline if trivial |
| 3 | **Redundant layers** | Pass-through wrappers, single-use abstractions | Inline or collapse |
| 4 | **Verbose syntax** | Nested if/else, manual loops, boilerplate | Use idiomatic language constructs |
| 5 | **Redundant state** | Duplicate caches, parallel data structures | Consolidate |
| 6 | **Over-split files** | Tiny files with one export used once | Merge when cohesion improves |

**Do not:**

- Remove error handling, validation, or security checks to save lines
- Merge functions with different semantics into ambiguous helpers
- Change public signatures without explicit user approval
- Trade readability for one-liner golf
- Shrink untested code without verification

For large repos, use [codebase-memory](../codebase-memory/SKILL.md) or targeted search to find duplication and dead paths without reading every file.

### Step 4 — Apply in small batches

1. Pick one candidate group (e.g. duplicate validators in one package).
2. Make the smallest correct diff.
3. Run tests and linters (see [test](../test/SKILL.md), [lint](../lint/SKILL.md)).
4. If anything fails, revert or fix before the next batch.

Prefer **fewer, clearer constructs** over **fewer characters**. A 3-line idiomatic expression beats a 1-line nested ternary.

### Step 5 — Simplification techniques

Apply as appropriate; stop when gains plateau or clarity suffers.

| Technique | Example |
|-----------|---------|
| **Inline single-use helper** | `getX()` called once → use expression at call site |
| **Merge duplicate branches** | Two functions differing by one param → one function with default |
| **Early return** | Deep nesting → guard clauses |
| **Data over code** | Repeated switch → map/lookup table |
| **Destructuring / pattern match** | Verbose field access → language idioms |
| **Remove intermediate variables** | Used once, name adds no clarity |
| **Collapse wrapper types** | Thin class wrapping one value with no behavior |

**Before (duplicate):**

```python
def validate_email(s): ...
def check_email(s): ...  # same logic

def create_user(data):
    if not validate_email(data["email"]): ...
```

**After (merged):**

```python
def valid_email(s): ...

def create_user(data):
    if not valid_email(data["email"]): ...
```

### Step 6 — Verify behavior parity (mandatory)

After each batch and before reporting done:

1. Run the **full** project test suite (or the scope's integration tests if whole-repo is impractical).
2. Run linters and formatters.
3. Re-check each **critical** item from Step 2 against tests or manual verification.
4. If public API changed, confirm user approval.

When shrinking security-sensitive paths, cross-check with [security-audit](../security-audit/SKILL.md) — simplification must not weaken validation or auth.

### Step 7 — Report savings

Deliver to the user:

```markdown
## Shrink summary
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| LOC (scope) | 4,820 | 4,105 | -15% |
| Files touched | — | 12 | — |

## Preserved (critical)
- All existing tests pass
- Public API unchanged
- ...

## Removed or simplified
- Deleted unused `legacy_parser.py` (142 LOC)
- Merged duplicate email validators (3 → 1)
- ...
```

Include `git diff --stat` when helpful.

## Shrink Checklist

- [ ] Baseline LOC and scope recorded
- [ ] Critical behaviors listed before edits
- [ ] No feature, security check, or error path removed without verification
- [ ] Dead code confirmed unused (search + tests), not just "looks unused"
- [ ] Duplicates merged to one canonical implementation
- [ ] Changes applied in testable batches
- [ ] Full test suite passes
- [ ] Linters pass
- [ ] Public API changes approved by user (if any)
- [ ] Savings summary delivered

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Deleting tests to shrink LOC | Keep or improve coverage |
| Code golf / unreadable one-liners | Idiomatic clarity |
| Big-bang rewrite in one commit | Small verified batches |
| Shrinking without running tests | Test after every batch |
| Removing "verbose" error messages users rely on | Shorten implementation, keep messages |
| Inlining everything | Keep helpers with real reuse or complex names |
| Touching vendored/generated code | Limit scope to project-owned source |

## Cross-References

- Tests before commit: [test](../test/SKILL.md)
- Lint gate: [lint](../lint/SKILL.md)
- Large-repo exploration: [codebase-memory](../codebase-memory/SKILL.md)
- Security-sensitive simplification: [security-audit](../security-audit/SKILL.md)

## Additional Resources

- Before/after examples and candidate patterns: [examples.md](examples.md)
