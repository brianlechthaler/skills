# Skill testing

Every skill in this repository is validated by automated tests in `tests/test_skills.py`. The checks run in CI on every push and pull request that touches skills, tests, or validation code.

## What is tested

Each skill (`<skill>/SKILL.md`) is exercised individually with parametrized pytest cases. For every skill, the suite verifies:

| Check | How |
|-------|-----|
| **Discovery & categorization** | `install.discover_skills()` finds the skill; `skill_categories.validate_skill_categories()` lists it exactly once |
| **Frontmatter** | YAML block with `name` matching the directory, valid `SKILL_NAME_RE`, and `description` ≥ 20 characters |
| **Body** | Non-empty markdown with a `#` heading and ≥ 100 characters of content |
| **Internal links** | Markdown links outside fenced/inline code resolve to real files; `../<skill>/SKILL.md` targets must exist in the repo |
| **Rule conversion** | `install.convert_skill_to_rule()` succeeds for Cursor, Claude, Windsurf, and plain formats |
| **Skill install** | `install.install_skill_for_agent(..., method="copy")` copies the skill into `.cursor/skills/<skill>/` |
| **Rule install** | `install.install_skill_as_rule_for_agent(..., "cursor")` writes `.cursor/rules/<skill>.mdc` |
| **README index** | `README.md` table links each skill as `[name](name/SKILL.md)` with no extras or omissions |

Validation logic lives in `skill_validate.py`. Link checking ignores content inside fenced code blocks and inline backticks so template examples (e.g. README skeletons in `document-project`) do not require files that only exist in target projects.

## Running tests locally

```bash
pip install pytest pytest-cov ruff
pytest tests/test_skills.py -v          # skill tests only
pytest                                  # full suite (install + skills + scripts)
ruff check skill_validate.py tests/
python scripts/sync_readme_skill_count.py --check
```

## Adding a new skill

1. Create `<skill>/SKILL.md` with valid frontmatter (`name` must match the directory).
2. Add the skill to `skill_categories.py` in exactly one category.
3. Add a table row to `README.md`.
4. Run `pytest tests/test_skills.py` — the new skill is picked up automatically via `discover_skills()`.
5. Run `python scripts/sync_readme_skill_count.py` to update skill-count markers.

## Fixes applied during test rollout

- **document-project** — Example README link wrapped in inline code so it is not validated as a repo-local path.
- **compiled-performance / interpreted-performance** — Removed broken `../canvas/SKILL.md` links; `canvas` is referenced as optional external tooling (same pattern as `security-audit`).
- **mcp-security** — Replaced broken `../review-security/SKILL.md` with plain-text optional reference plus link to `security-audit`.
