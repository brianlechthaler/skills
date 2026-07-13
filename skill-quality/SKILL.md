---
name: skill-quality
description: >-
  Analyze agent skill quality (SKILL.md), score against a structured rubric,
  suggest prioritized improvements, and optionally implement fixes. Use when
  reviewing, auditing, or improving skills; when the user asks to evaluate
  skill quality, tighten skill instructions, or fix skill validation errors;
  or when adding or refactoring skills in this repository or a skills project.
---

# Skill Quality

Conduct a **structured quality review** of one or more agent skills (`SKILL.md` and supporting files). Run automated validation first, score against a rubric, deliver prioritized recommendations, and optionally apply fixes.

This skill reviews **skill instructions** — not application code. For trimming token cost without losing policy, also apply [prompt-conciseness](../prompt-conciseness/SKILL.md). For skills that embed security policies, cross-check with [prompt-security](../prompt-security/SKILL.md).

## Implement Mode (decide first)

| User intent | Behavior after review |
|-------------|----------------------|
| Default — "review this skill", "analyze skill quality", "audit skills", etc. | Deliver findings and recommendations, then **ask** whether to implement improvements |
| Explicit implement — "review and fix", "improve and implement", "apply recommendations", "fix validation errors" | **Skip the prompt** — implement approved-priority fixes immediately after the report |

When implementing:

1. Fix in priority order: Critical → High → Medium → Low
2. Re-run validation after each batch (`python skill_validate.py` or `pytest tests/test_skills.py` when in this repo)
3. Follow [lint](../lint/SKILL.md) when editing Python validation code; follow repo skill conventions for `SKILL.md` edits
4. Do **not** commit unless the user asks — use [github-publish](../github-publish/SKILL.md) when they do

When prompting (default), use AskQuestion when available:

- **Prompt**: "Implement the recommended skill improvements?"
- **Options**: "Yes — implement all", "Yes — Critical and High only", "No — report only"

If AskQuestion is unavailable, ask conversationally with the same options.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| Reviewing `SKILL.md` files (single skill or batch) | Reviewing general user rules or `AGENTS.md` (use [prompt-conciseness](../prompt-conciseness/SKILL.md)) |
| User asks to improve, audit, or score skill quality | Writing application features unrelated to skills |
| Fixing skill validation / install failures in a skills repo | Converting skills to rules only (installer handles that) |
| Adding a new skill and wanting it to match repo standards | One-line typo in unrelated project code |

When unsure and the target is a `SKILL.md` (or skill directory), default to applying this skill.

## Workflow

Copy and track progress:

```
Skill quality review:
- [ ] Phase 0: Scope — which skills, repo context, implement mode
- [ ] Phase 1: Automated validation — structure, links, rule conversion
- [ ] Phase 2: Rubric scoring — clarity, triggers, workflow, completeness
- [ ] Phase 3: Consistency — naming, cross-refs, repo integration
- [ ] Phase 4: Efficiency — redundancy, token cost, scannable structure
- [ ] Phase 5: Security — policy skills only (prompt-security pass)
- [ ] Phase 6: Report — prioritized findings with scores
- [ ] Phase 7: Implement — prompt or auto-fix
```

Run phases **in order**. Do not skip automated validation — structural failures block reliable agent use.

### Phase 0 — Scope

Clarify before reading:

- **Target** — one skill path, a list, or all skills in a repo
- **Context** — skills collection (e.g. this repo) vs. ad-hoc project skill
- **Implement mode** — default (report + ask) vs. explicit implement
- **Constraints** — preserve behavior, no scope expansion, must pass CI

For this repository, skills live in `<skill>/SKILL.md` with optional `examples.md`, `checklist.md`, etc. Discovery: `python3 install.py --list` or `install.discover_skills(repo_root)`.

### Phase 1 — Automated validation

Run every check that exists for the target repo.

**In this skills repository:**

```bash
python3 -c "
from pathlib import Path
import skill_validate
root = Path('.')
for skill in ['TARGET_SKILL']:
    r = skill_validate.validate_skill(skill, root)
    print(skill, 'OK' if r.ok else r.errors)
"
pytest tests/test_skills.py -k TARGET_SKILL -v
```

**Checks enforced here** (see `skill_validate.py` and `docs/features/skill-testing.md`):

| Check | Failure impact |
|-------|----------------|
| YAML frontmatter with `name` matching directory | Skill won't install or discover correctly |
| `description` ≥ 20 chars, valid `SKILL_NAME_RE` | Poor or broken agent triggering |
| Body ≥ 100 chars, `#` heading | Empty or unusable skill body |
| Markdown links resolve (outside code literals) | Broken cross-skill navigation |
| Rule conversion (cursor, claude, windsurf, plain) | `--as-rule` install breaks |
| README table link + single category (this repo) | Index and CI out of sync |

Record all automated errors as **Critical** findings until fixed.

### Phase 2 — Rubric scoring

Score each skill **1–5** per dimension (5 = exemplar). Full criteria: [rubric.md](rubric.md).

| Dimension | What good looks like |
|-----------|---------------------|
| **Trigger clarity** | `description` states when to use; "When This Applies" table with applies / does-not |
| **Actionability** | Numbered workflow, copy-paste progress checklist, concrete commands |
| **Structure** | `#` title, scannable sections, tables for comparisons, anti-patterns |
| **Completeness** | Core rules, boundaries, cross-refs, optional resources file |
| **Consistency** | Matches peer skills in the same repo (tone, implement-mode pattern, link style) |
| **Maintainability** | No stale paths, examples in `examples.md` not bloating `SKILL.md` |

Compute an **overall score** (average of dimensions, one decimal). Flag any dimension ≤ 2 as **High** priority to address.

### Phase 3 — Consistency

Compare the skill to **2–3 strong peers** in the same repo (e.g. [orchestrate](../orchestrate/SKILL.md), [security-audit](../security-audit/SKILL.md), [lint](../lint/SKILL.md)).

| Signal | Issue if missing |
|--------|------------------|
| Implement / fix mode section | User intent for "report only" vs "fix" is ambiguous |
| "When This Applies" table | Agent over- or under-applies the skill |
| Progress checklist block | Long workflows stall without trackable steps |
| Anti-patterns table | Same mistakes repeat across sessions |
| Cross-references to related skills | Duplicated or conflicting guidance |
| `examples.md` for long samples | `SKILL.md` is too long for context budget |

**This repo only:** skill appears exactly once in `skill_categories.py` and in `README.md` with link `[name](name/SKILL.md)`.

### Phase 4 — Efficiency

Apply [prompt-conciseness](../prompt-conciseness/SKILL.md) **lightly** — skills need enough detail to be actionable.

Look for:

- Duplicate rules stated in prose and again in tables
- Long narrative where a table or checklist suffices
- Multiple examples inline — move to [examples.md](examples.md)
- Vague triggers ("use when helpful") — tighten `description` and when-table

Do **not** compress away implement-mode rules, severity guides, or mandatory checklists.

### Phase 5 — Security (conditional)

When the skill defines **policies, refusal rules, or disclosure boundaries**, run a quick [prompt-security](../prompt-security/SKILL.md) pass:

- Non-disclosure and instruction hierarchy preserved
- No contradictory "ignore previous instructions" patterns in examples
- Security-critical negations ("never", "do not") remain explicit after edits

Skip this phase for purely operational skills (e.g. docker, lint).

### Phase 6 — Report

Present a structured review. Every finding MUST include:

| Field | Content |
|-------|---------|
| ID | `SKQ-001`, `SKQ-002`, … |
| Priority | Critical / High / Medium / Low |
| Dimension | e.g. Trigger clarity, Validation, Structure |
| Location | `skill-name/SKILL.md` section or line |
| Evidence | Quote or describe the gap |
| Recommendation | Specific edit — not "improve clarity" |
| Effort | S / M / L |

Include a summary table:

```markdown
## Skill quality summary — `<skill-name>`

| Dimension | Score (1–5) | Notes |
|-----------|-------------|-------|
| Trigger clarity | 4 | ... |
| ... | ... | ... |
| **Overall** | **3.8** | |

Automated validation: pass / N errors
Findings: C critical, H high, M medium, L low
```

For multi-skill audits, sort skills by overall score (lowest first) and list top 3 improvements per skill.

End with:

```
Total: N findings (C critical, H high, M medium, L low)
```

Sample reports: [examples.md](examples.md)

### Phase 7 — Implement

**If implement mode** (user requested it): apply fixes per priority. No prompt.

**If default mode**: ask whether to implement. On "Yes", edit skills per recommendations.

When implementing:

- Prefer minimal diffs — one concern per commit when the user commits
- Preserve skill `name` === directory name
- After edits in this repo: `pytest tests/test_skills.py -v` and `python scripts/sync_readme_skill_count.py --check` if skill count changed
- Re-score affected dimensions and note deltas in the closing summary

**Adding a new skill in this repo** also requires:

1. `<skill>/SKILL.md` with valid frontmatter
2. Entry in `skill_categories.py` (exactly one category)
3. Row in `README.md` skills table
4. `python scripts/sync_readme_skill_count.py` to refresh count markers

## Priority Guide

| Priority | Criteria |
|----------|----------|
| **Critical** | Automated validation failure; broken install; wrong `name`; misleading trigger that causes harmful behavior |
| **High** | Dimension score ≤ 2; missing when-table or workflow; no implement-mode clarity for fix-oriented skills |
| **Medium** | Redundancy, weak cross-refs, missing anti-patterns, bloated inline examples |
| **Low** | Style nits, optional examples.md split, minor wording polish |

When uncertain, **round up** — unclear skills cause agent mistakes.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Reviewing only the description line | Full body, links, supporting files, validation output |
| Generic advice ("make it clearer") | Cite section; propose replacement text |
| Implementing large rewrites without user consent (default mode) | Report first; ask |
| Stripping safety or scope rules for brevity | [prompt-conciseness](../prompt-conciseness/SKILL.md) with parity check |
| Ignoring rule-conversion failures | Fix `SKILL.md` structure until all formats convert |
| Adding skills to this repo without category + README | Follow Phase 7 checklist |

## Cross-References

- Repo validation and CI: `docs/features/skill-testing.md`, `skill_validate.py`
- Shorten skill text: [prompt-conciseness](../prompt-conciseness/SKILL.md)
- Policy-heavy skills: [prompt-security](../prompt-security/SKILL.md)
- Publishing fixes: [github-publish](../github-publish/SKILL.md)
- Parallel multi-skill overhauls: [orchestrate](../orchestrate/SKILL.md)

## Additional Resources

- Scoring criteria and per-dimension checklists: [rubric.md](rubric.md)
- Before/after review examples: [examples.md](examples.md)
