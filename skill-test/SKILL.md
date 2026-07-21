---
name: skill-test
description: >-
  Create and maintain automated tests for agent skills — validate SKILL.md
  structure, links, install paths, and rule conversion; extend the test harness
  when needed. Use when adding or editing skills, writing skill validation
  tests, debugging skill test failures in CI, or when the user asks to test
  agent skills or skill directories.
---

# Skill Test

Create and maintain **automated tests for agent skills** in this repository. Every skill (`<skill>/SKILL.md`) is validated by parametrized pytest cases in `tests/test_skills.py` and shared helpers in `skill_validate.py`.

For general TDD and coverage on production code, follow [test](../test/SKILL.md). For lint gates before commit, follow [lint](../lint/SKILL.md).

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| Adding a new skill directory and `SKILL.md` | Editing unrelated project code with its own test suite |
| Changing skill frontmatter, body, or internal links | Pure README prose with no skill changes |
| Extending `skill_validate.py` or `tests/test_skills.py` | Skills in other repos (adapt patterns, do not assume this harness) |
| CI failures in `tests/test_skills.py` or `skill_validate.py` | User explicitly opts out of skill validation |
| User asks to "test skills" or "add skill tests" | |

When unsure, **run `pytest tests/test_skills.py`** after any skill change.

## What Is Tested Automatically

New skills are picked up via `install.discover_skills()` — no manual test registration per skill name. For each discovered skill, the suite verifies:

| Check | Module / test |
|-------|----------------|
| Discovery and categorization | `install.discover_skills()`, `skill_categories.validate_skill_categories()` |
| YAML frontmatter (`name`, `description`) | `skill_validate.validate_skill_frontmatter()` |
| Body length and heading | `skill_validate.validate_skill_body()` |
| Internal markdown links | `skill_validate.validate_markdown_links()` |
| Rule conversion (Cursor, Claude, Windsurf, plain) | `skill_validate.validate_rule_conversion()` |
| Skill install (copy method) | `test_skill_install_copy` |
| Rule install (Cursor `.mdc`) | `test_skill_rule_install_cursor` |
| Skills catalog index | `skill_validate.validate_readme_skills()` on `docs/features/skills-catalog.md` |

Full reference: [docs/features/skill-testing.md](../docs/features/skill-testing.md).

## Workflow: Add a New Skill

Run steps **in order**. Do not skip validation before commit.

```
Skill test progress:
- [ ] `<skill>/SKILL.md` created with valid frontmatter (`name` matches directory)
- [ ] Skill added to `skill_categories.py` in exactly one category
- [ ] skills-catalog.md category table row added (`[skill](../../skill/SKILL.md)`)
- [ ] `pytest tests/test_skills.py -v` passes (new skill auto-discovered)
- [ ] `python scripts/sync_readme_skill_count.py` run to update count markers
- [ ] `ruff check` and `ruff format --check` pass on changed Python files
```

### Frontmatter requirements

- `name` must match the directory name and `install.SKILL_NAME_RE` (lowercase, hyphens)
- `description` must be at least 20 characters
- Body must have a `#` heading and at least 100 characters after frontmatter

### Link rules

Markdown links outside fenced code and inline backticks must resolve:

- `../<other-skill>/SKILL.md` — target skill must exist in the repo
- Relative paths like `examples.md` — file must exist in the skill directory
- Wrap template or example links in backticks or fenced blocks so they are not validated (see `document-project`)

## Workflow: Extend the Test Harness

Add custom tests only when automatic validation is insufficient — e.g. new install behavior, a new rule format, or skill-specific helper scripts.

1. **Red** — Write a failing test in `tests/` that describes the new behavior.
2. **Green** — Implement the minimum change in `skill_validate.py`, `install.py`, or the relevant module.
3. **Refactor** — Keep tests parametrized over `ALL_SKILLS` when the check applies to every skill.

Prefer extending existing validators over one-off per-skill tests:

```python
# tests/test_skills.py — pattern for per-skill checks
@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_structure_and_content(skill: str, known_skills: frozenset[str]) -> None:
    result = skill_validate.validate_skill(skill, ROOT, known_skills)
    assert result.ok, f"{skill} validation failed:\n  - " + "\n  - ".join(result.errors)
```

For isolated edge cases, add focused unit tests (see `test_validate_skill_frontmatter_detects_issues` and `test_validate_markdown_links_detects_broken_cross_skill` in `tests/test_skills.py`).

Update `docs/features/skill-testing.md` when adding a new automatic check so contributors know what CI enforces.

## Workflow: Fix Skill Test Failures

When CI or local pytest reports a skill failure:

1. Read the full error list from `SkillValidationResult.errors` — fix **all** listed issues, not just the first.
2. Common fixes:

| Error | Fix |
|-------|-----|
| `name does not match directory` | Align `name` in frontmatter with folder name |
| `description too short` | Expand description to ≥ 20 characters |
| `body too short` / `missing top-level markdown heading` | Add `#` heading and substantive content |
| `broken cross-skill link` | Fix `../skill/SKILL.md` path or remove link |
| `broken local link` | Add the missing file or wrap example in backticks |
| `skills-catalog.md missing table link` | Add row to the correct category table in `docs/features/skills-catalog.md` |
| `skills missing from SKILL_CATEGORIES` | Add skill to exactly one tuple in `skill_categories.py` |

3. Re-run `pytest tests/test_skills.py -v` until green.
4. If `sync_readme_skill_count.py --check` fails, run `python scripts/sync_readme_skill_count.py` without `--check`.

For CI debug on GitHub Actions, use [ci-debug](../ci-debug/SKILL.md).

## Commands

```bash
# Skill tests only
pytest tests/test_skills.py -v

# Full suite (install + skills + scripts)
pytest

# Lint validation code
ruff check skill_validate.py tests/ skill_categories.py
ruff format --check skill_validate.py tests/ skill_categories.py

# Verify README skill count markers
python scripts/sync_readme_skill_count.py --check

# Update README skill count (after adding a skill)
python scripts/sync_readme_skill_count.py
```

## Pre-Commit Checklist

Copy and complete before committing skill or test harness changes:

```
Skill test gates:
- [ ] `pytest tests/test_skills.py` passes
- [ ] New skill in `skill_categories.py` (exactly one category)
- [ ] skills-catalog.md table row added; skill count synced
- [ ] No broken markdown links in SKILL.md (outside code literals)
- [ ] ruff check/format pass on changed Python files
```

Do not commit skill changes with failing `test_skills.py` or README validation errors.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Hard-code skill names in tests when parametrization works | Use `ALL_SKILLS` and `discover_skills()` |
| Skip skills-catalog or category updates | Both are enforced by tests |
| Put example links in prose without backticks | Wrap in `` ` `` or fenced blocks |
| Loosen validation to make one skill pass | Fix the skill content or add a targeted unit test |
| Assume local pass without running pytest | Always run `pytest tests/test_skills.py` |
