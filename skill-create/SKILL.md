---
name: skill-create
description: >-
  Create new agent skills from scratch — name and scope the skill, write
  SKILL.md with valid frontmatter, register in skill_categories.py and README,
  run validation, open a PR, and merge when CI is green. Use when the user asks
  to add a skill, create a new skill, author SKILL.md, or bootstrap a skills
  project entry.
---

# Skill Create

End-to-end workflow for **adding a new agent skill** to this repository (or adapting the same steps in another skills project). Covers naming, authoring, repo registration, validation, publishing, and merge.

For automated test harness details, follow [skill-test](../skill-test/SKILL.md). For quality review after drafting, follow [skill-quality](../skill-quality/SKILL.md). For git and PR mechanics, follow [github-publish](../github-publish/SKILL.md).

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| User asks to create, add, or author a new skill | Editing an existing skill only (use [skill-quality](../skill-quality/SKILL.md)) |
| Bootstrapping `<skill>/SKILL.md` in this repo | Writing application code unrelated to skills |
| Registering a skill in `skill_categories.py` and `README.md` | Extending `skill_validate.py` (use [skill-test](../skill-test/SKILL.md)) |
| Opening a PR for a new skill and merging when CI passes | Skills in external repos (adapt steps; validation commands may differ) |

When unsure and the deliverable is a new `SKILL.md`, apply this skill.

## Core Rules

1. **One skill per directory** — lowercase name with hyphens; `name` in frontmatter must match the folder exactly.
2. **Register everywhere** — `SKILL.md`, exactly one entry in `skill_categories.py`, and a row in the matching `README.md` category table.
3. **Validate before commit** — run skill tests and sync README count markers; do not push failing validation.
4. **Feature branch + PR** — never commit new skills directly to the default branch.
5. **Merge when CI is green** — when the user requests merge-on-green (or this skill is invoked with that intent), merge without asking once all required checks pass.

## Workflow Checklist

Copy and track progress:

```
Skill create:
- [ ] Phase 0: Scope — purpose, triggers, category, skill name
- [ ] Phase 1: Author — `<skill>/SKILL.md` with frontmatter and body
- [ ] Phase 2: Register — skill_categories.py + README.md table row
- [ ] Phase 3: Validate — pytest, ruff, README count sync
- [ ] Phase 4: Publish — branch, commit, push, open PR
- [ ] Phase 5: Merge — wait for CI green, then merge
```

Run phases **in order**. Do not skip validation or registration.

### Phase 0 — Scope

Before writing files, decide:

| Decision | Guidance |
|----------|----------|
| **Skill name** | Lowercase, hyphens, matches `install.SKILL_NAME_RE` (e.g. `docker-optimize`, `skill-create`) |
| **Purpose** | One focused workflow — split broad topics into separate skills |
| **Triggers** | What the agent should match on; becomes the `description` frontmatter field (≥ 20 chars) |
| **Category** | Pick one from `skill_categories.py` — DevOps, GitHub, Documentation, Testing & Quality, etc. |
| **Overlap** | Check `python3 install.py --list` — extend an existing skill instead of duplicating |

Write a one-line purpose statement and 3–5 trigger phrases before drafting content.

### Phase 1 — Author

Create `<skill>/SKILL.md` with YAML frontmatter and markdown body.

**Frontmatter template:**

```yaml
---
name: <skill-name>
description: >-
  <What the skill does in one or two sentences. Include concrete trigger phrases
  — when to use, when the user asks for X, etc. Minimum 20 characters.>
---
```

**Body structure** (match peer skills in the same category):

```markdown
# Skill Title

Brief intro — what this skill accomplishes and how it relates to peers.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| ... | ... |

## Workflow

Progress checklist or numbered steps.

## Commands

Concrete shell commands when relevant.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| ... | ... |
```

**Authoring rules:**

| Rule | Detail |
|------|--------|
| `name` | Must equal directory name |
| `description` | ≥ 20 characters; state **when** to use the skill |
| Body | `#` heading required; ≥ 100 characters after frontmatter |
| Links | `../other-skill/SKILL.md` for cross-skill refs; relative paths for local files |
| Examples in prose | Wrap template links in backticks or fenced blocks so validators skip them |
| Optional files | `examples.md`, `rubric.md`, `checklist.md` in the skill directory when content is long |

Strong peers to emulate: [orchestrate](../orchestrate/SKILL.md), [lint](../lint/SKILL.md), [skill-test](../skill-test/SKILL.md).

### Phase 2 — Register

1. **`skill_categories.py`** — add the skill name to exactly **one** category tuple (alphabetical order within the tuple is conventional).
2. **`README.md`** — add a table row in the matching category section:

```markdown
| [<skill-name>](<skill-name>/SKILL.md) | One-line summary of what the skill does. |
```

3. **Skill count** — run `python3 scripts/sync_readme_skill_count.py` to update `<!-- skill-count:N -->` markers and the `## Skills (N)` heading.

### Phase 3 — Validate

Run all gates before committing:

```bash
python3 -m pytest tests/test_skills.py -v
python3 -m pytest
python3 -m ruff check install.py skill_categories.py skill_validate.py scripts/ tests/
python3 -m ruff format --check install.py skill_categories.py skill_validate.py scripts/ tests/
python3 scripts/sync_readme_skill_count.py --check
```

Fix every error from `skill_validate.validate_skill()` — common failures:

| Error | Fix |
|-------|-----|
| `name does not match directory` | Align frontmatter `name` with folder |
| `description too short` | Expand to ≥ 20 characters with trigger phrases |
| `body too short` / `missing top-level markdown heading` | Add `#` title and substantive sections |
| `broken cross-skill link` | Fix `../skill/SKILL.md` path |
| `skills missing from SKILL_CATEGORIES` | Add to exactly one category |
| `README missing table link` | Add row to correct category table |

Optionally run [skill-quality](../skill-quality/SKILL.md) on the draft before opening the PR.

### Phase 4 — Publish

From the repo root on a feature branch (not the default branch):

```bash
git checkout -b cursor/<descriptive-name>-<suffix>   # or feat/add-<skill>-skill
git add <skill>/ skill_categories.py README.md
git commit -m "Add <skill-name> skill"
git push -u origin <branch-name>
gh pr create --draft --title "Add <skill-name> skill" --body "..."
```

PR body should note: skill purpose, category, validation commands run, and that merge is requested when CI is green.

Mark draft PR ready for review when local gates pass.

### Phase 5 — Merge when CI is green

When the user says **merge when CI is green** (or this skill is invoked with merge intent):

1. Watch CI until all required checks pass:

```bash
gh pr checks --watch
```

2. If CI fails, fix issues on the same branch, push, and re-watch until green.
3. **Merge without asking** — the user already requested automated merge:

```bash
gh pr merge --merge --delete-branch
```

4. Summarize: PR URL, checks status, merge result.

If the user did **not** request auto-merge, follow [github-publish](../github-publish/SKILL.md): ask for approval after CI is green.

**This repository CI** runs on PRs that touch `**/SKILL.md`, `skill_categories.py`, `README.md`, tests, and related paths — see `.github/workflows/test.yml` and `lint.yml`.

## Pre-Commit Checklist

```
Skill create gates:
- [ ] `<skill>/SKILL.md` — valid frontmatter, heading, body length
- [ ] skill_categories.py — exactly one category
- [ ] README.md — category table row added
- [ ] sync_readme_skill_count.py — count markers updated
- [ ] pytest tests/test_skills.py passes
- [ ] ruff check/format pass on changed files
```

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Creating a skill without README or category entry | Register in both — CI enforces this |
| Vague `description` ("use when helpful") | Concrete triggers and user phrases |
| One mega-skill covering unrelated workflows | Split into focused skills |
| Example links in prose without backticks | Wrap in `` ` `` or fenced blocks |
| Pushing before `pytest tests/test_skills.py` | Always validate locally first |
| Merging with failing CI | Fix or report blocker; only merge when green |

## Cross-References

- Validation and CI: [skill-test](../skill-test/SKILL.md), `docs/features/skill-testing.md`
- Quality review: [skill-quality](../skill-quality/SKILL.md)
- Git and PR workflow: [github-publish](../github-publish/SKILL.md)
- Lint before commit: [lint](../lint/SKILL.md)
- Agent Skills spec: https://agentskills.io/
