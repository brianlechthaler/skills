---
name: github-merge-all
description: >-
  Find every open pull request in a repository, resolve merge conflicts on each
  branch, wait for CI when required, and merge PRs one at a time. Use when the
  user asks to merge all open PRs, clear the PR backlog, land every open pull
  request, or automatically merge and resolve conflicts across open branches.
---

# GitHub Merge All

Process every open PR in the current repository: sync with the default branch, resolve conflicts, pass gates, merge.

## Core Rules

1. **Use `gh` for all GitHub operations** — list PRs, check out branches, watch CI, merge.
2. **One PR at a time** — finish (merge or skip with reason) before starting the next. Re-list PRs after each merge; bases and conflicts change.
3. **Merge without asking** when this skill is invoked — the user already requested automated merging. Still skip PRs you cannot safely land and summarize blockers.
4. **Fix conflicts on the PR branch** — never force-push to the default branch; push resolution commits only to the feature branch.
5. **Prefer integrating all changes** — when multiple PRs touch the same files (e.g. `skill_categories.py`, `README.md`), resolve conflicts by keeping **every** PR's intended additions, not by picking one side.
6. **Follow project gates** — run [test](../test/SKILL.md) and [lint](../lint/SKILL.md) after conflict resolution or substantive fixes; use [docker](../docker/SKILL.md) when the project runs tooling in containers.
7. **Mark draft PRs ready** before merge when the user asked to merge all open PRs.

## Prerequisites

```bash
gh auth status
git remote -v
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
```

If `gh` is not authenticated, run `gh auth login` and stop until the user completes it.

## Workflow Checklist

Copy and track:

```
Merge all open PRs:
- [ ] Open PRs listed and ordered (oldest first unless user specified)
- [ ] Each PR: synced → conflicts resolved → validated → CI green → merged or skipped
- [ ] Final summary shared (merged, skipped, blockers)
```

## 1. Discover Open PRs

List all open PRs (any author):

```bash
gh pr list \
  --state open \
  --json number,title,headRefName,baseRefName,isDraft,labels,createdAt,url,mergeable,mergeStateStatus \
  --limit 100
```

Record for each: number, title, branch, draft status, mergeable state, URL, `createdAt`.

**Exclude** only when the user explicitly asks (e.g. "skip drafts", "only Dependabot") — otherwise include every open PR.

Default order: **oldest first** (`createdAt` ascending). Re-run the list command after each merge.

## 2. Detect Merge Strategy

Inspect recent merged PRs:

```bash
gh pr list --state merged --limit 5 --json number,title,mergeCommit
```

| Signal | Strategy |
|--------|----------|
| Single-parent squash-style commits, or repo uses squash merges | `gh pr merge --squash --delete-branch` |
| Rebase-only policy in CONTRIBUTING or repo settings | `gh pr merge --rebase --delete-branch` |
| Default merge commits | `gh pr merge --merge --delete-branch` |

When unsure, use `--merge`.

## 3. Process Each PR

For each PR in order:

### 3a. Preflight

```bash
gh pr view <number> --json title,body,files,mergeable,mergeStateStatus,statusCheckRollup,isDraft,headRefName,baseRefName
```

**Skip without merge** (optional comment on PR) when:

- Required checks are failing and failures are outside what conflict resolution or a minimal sync fix can address
- The PR is explicitly blocked (e.g. "do not merge", "WIP", requested changes you cannot satisfy)
- Conflict resolution would discard unrelated work or require rewriting another PR's intent

Otherwise continue.

### 3b. Check out the PR branch

```bash
git fetch origin
gh pr checkout <number>
```

Stash or commit local work first if checkout fails.

### 3c. Sync with the default branch (conflict prevention and resolution)

Always merge the latest default branch into the PR branch before merging the PR:

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin
git merge "origin/$DEFAULT"
```

**If the merge succeeds with no conflicts**, proceed to validation.

**If conflicts occur**, resolve them on the PR branch:

1. Run `git status` and list conflicted files.
2. For each file, read both sides and the PR's intent (`gh pr diff <number>`, PR body, changed paths).
3. **Integrate both sides** when safe — e.g. add all new skills to `skill_categories.py` and all README table rows; do not drop another merged PR's entries.
4. Remove conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
5. Run project validation (tests, lint, category sync scripts if applicable).
6. Commit the resolution on the PR branch:

```bash
git add <resolved-files>
git commit -m "$(cat <<'EOF'
merge: resolve conflicts with origin/<default-branch>

EOF
)"
git push origin HEAD
```

Do **not** use `git merge --abort` unless you are abandoning this PR — fix forward.

**Common conflict patterns in this repo:**

| File | Resolution |
|------|------------|
| `skill_categories.py` | Include every new skill tuple from both sides in the correct category |
| `README.md` | Keep all new skill rows; run `python3 scripts/sync_readme_skill_count.py` to fix the count |
| `tests/` | Combine assertions; ensure `validate_skill_categories` passes |

After pushing, refresh merge state:

```bash
gh pr view <number> --json mergeable,mergeStateStatus
```

### 3d. Validate locally

Discover and run the project's standard checks (from CI workflows, `Makefile`, or `package.json`). For this skills repo:

```bash
python3 scripts/sync_readme_skill_count.py   # when README skill count changed
python3 -m pytest tests/ -q
```

Fix any failures caused by the sync or conflict resolution; commit and push on the PR branch.

### 3e. Wait for CI

```bash
gh pr checks <number> --watch
```

If CI fails after your push:

- Fetch logs: `gh run list --branch "$(git branch --show-current)" --limit 3` then `gh run view <id> --log-failed`
- Fix within PR scope, push, re-watch.
- If failures are flaky or unrelated after reasonable fixes, document and skip.

### 3f. Mark ready and merge

Draft PRs must be marked ready before merge:

```bash
gh pr ready <number>   # when isDraft is true
```

When local validation passes and required CI checks are green:

```bash
gh pr merge <number> --merge --delete-branch
# or --squash / --rebase per repo convention
```

Return to the default branch before the next PR:

```bash
git checkout "$DEFAULT"
git pull origin "$DEFAULT"
```

Re-list open PRs and continue until none remain or all are skipped with documented reasons.

## 4. Final Report

Return a structured summary:

```markdown
## Merge-all summary

**Repository:** <owner/repo>
**Default branch:** <branch>

### Merged (N)
- #123 — <title> (no conflicts)
- #124 — <title> (resolved conflicts in skill_categories.py, README.md)

### Skipped (M)
- #125 — <title> — reason: CI failing on unrelated infra

### Blockers
- <anything needing user decision>
```

## Integration with Other Skills

| Situation | Skill |
|-----------|-------|
| Dependabot-only backlog | [dependabot-merge](../dependabot-merge/SKILL.md) — safer dep-specific checks |
| CI failures during merge | [ci-debug](../ci-debug/SKILL.md) — when present in the repo |
| Code fixes on a PR branch | [test](../test/SKILL.md), [lint](../lint/SKILL.md) |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Merge with failing required CI | Fix on branch or skip with reason |
| Resolve conflicts by dropping other PRs' additions | Integrate all intended changes |
| Parallel checkouts of multiple PR branches | One PR at a time |
| Force-push to the default branch | Push only to feature branches |
| Batch-merge without re-listing | Re-list after each merge |
| Leave draft PRs unmerged when user asked to merge all | `gh pr ready` then merge |
| `git merge --abort` after starting conflict resolution | Fix forward unless abandoning the PR |

## Additional Resources

- Command reference and examples: [examples.md](examples.md)
