---
name: dependabot-merge
description: >-
  Find open Dependabot pull requests for a repository, verify each dependency
  update is safe, apply code changes required for new versions, and merge PRs
  when tests and CI pass. Use when the user asks to merge Dependabot PRs,
  update dependencies, clear a Dependabot backlog, or safely bump package
  versions from automated dependency PRs.
---

# Dependabot Merge

Process every open Dependabot PR for the current repository: assess safety, fix breakage, pass gates, merge.

## Core Rules

1. **Use `gh` for all GitHub operations** — list PRs, check out branches, watch CI, merge.
2. **One PR at a time** — finish (merge or skip with reason) before starting the next. Re-list PRs after each merge; bases and conflicts change.
3. **Never merge unsafe updates** — failing tests, unfixable breaking changes, or CI you cannot green stay open; report why.
4. **Fix code on the Dependabot branch** — push migration fixes to the PR branch, not a new branch.
5. **Never force-push to the default branch** — only push to the Dependabot feature branch.
6. **Follow project gates** — run [test](../test/SKILL.md) and [lint](../lint/SKILL.md) when fixing code; use [docker](../docker/SKILL.md) when the project runs tooling in containers.
7. **Merge without asking** when this skill is invoked — the user already requested automated merging. Still skip PRs you cannot safely land and summarize blockers.

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
Dependabot merge:
- [ ] Open Dependabot PRs listed and prioritized
- [ ] Each PR: assessed → checked out → validated → fixed (if needed) → CI green → merged or skipped
- [ ] Final summary shared (merged, skipped, blockers)
```

## 1. Discover Dependabot PRs

List open PRs authored by Dependabot:

```bash
gh pr list \
  --author "app/dependabot" \
  --state open \
  --json number,title,headRefName,baseRefName,labels,createdAt,url \
  --limit 100
```

If that returns nothing, also try:

```bash
gh pr list --label "dependencies" --state open \
  --json number,title,headRefName,baseRefName,labels,createdAt,url
```

Filter to PRs that are actually dependency updates (title usually starts with `Bump` or `build(deps)`).

Record for each: number, title, bump type (patch / minor / major), ecosystem (npm, pip, cargo, go, docker, github-actions, etc.), URL.

## 2. Prioritize

Process in this order unless the user specifies otherwise:

| Priority | Kind | Rationale |
|----------|------|-----------|
| 1 | Security advisories (`security` label or Dependabot security PRs) | Close known vulnerabilities first |
| 2 | Patch bumps | Lowest risk |
| 3 | Minor bumps | Usually backward compatible |
| 4 | Major bumps | Highest breakage risk — extra changelog review |
| 5 | GitHub Actions / CI deps | Often isolated from app code |

Within the same tier, process **oldest first** (`createdAt`).

**Group awareness:** merging one npm PR may auto-close or conflict with others. After each merge, re-run the list command.

## 3. Process Each PR

For each PR in priority order:

### 3a. Assess safety (before checkout)

```bash
gh pr view <number> --json title,body,files,mergeable,mergeStateStatus,statusCheckRollup
```

Read the PR body for:

- Version range (`1.2.3` → `1.2.4` vs `1.x` → `2.0.0`)
- Release notes / changelog links Dependabot included
- CVE or advisory text for security updates

**Skip without merge** (comment on PR optional) when:

- `mergeable` is `CONFLICTING` and conflict resolution would change unrelated app logic — report for human review
- Major bump with documented breaking changes you cannot reasonably fix in this session
- Update touches a dependency the project explicitly pins or vendors for compatibility reasons (check README, comments, or `package.json` `overrides` / `resolutions`)
- PR is a grouped update spanning multiple majors across unrelated packages — split or defer

Otherwise continue.

### 3b. Check out the PR branch

```bash
git fetch origin
gh pr checkout <number>
```

If checkout fails due to conflicts with local work, stash or commit local changes first.

### 3c. Understand the change

```bash
gh pr diff <number> --name-only
gh pr diff <number>
```

Identify:

- Lockfile-only vs manifest + lockfile
- Direct vs transitive dependency
- Whether app source imports the updated package

For **major** bumps or unfamiliar packages, read the linked changelog / migration guide (release notes URL in PR body, or `https://github.com/<owner>/<repo>/releases`).

### 3d. Install and validate locally

Use the project's standard install command after dependency file changes:

| Ecosystem | Typical install |
|-----------|-----------------|
| npm/pnpm/yarn | `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable` |
| Python | `pip install -e .`, `uv sync`, `poetry install` |
| Go | `go mod download` |
| Rust | `cargo fetch` |

Then run the project's test and lint commands (from `package.json`, `Makefile`, or CI workflows). Mirror CI when unsure.

If the [docker](../docker/SKILL.md) skill applies, run install, test, and lint **inside the container**.

### 3e. Fix breakage

When tests or build fail due to the new version:

1. Read error output and map failures to breaking API changes.
2. Change **application code** (or project config) — not the dependency version rolled back.
3. Keep fixes minimal and scoped to what the upgrade requires.
4. Follow [test](../test/SKILL.md) and [lint](../lint/SKILL.md) for any code you change.
5. Commit on the PR branch:

```bash
git add <relevant-files>
git commit -m "$(cat <<'EOF'
fix: adapt code for <package>@<new-version>

EOF
)"
git push origin HEAD
```

6. Re-run local tests and lint until green.

Do **not** widen scope into unrelated refactors.

### 3f. Wait for CI

```bash
gh pr checks <number> --watch
```

If CI fails:

- Pull failure logs: `gh run list --branch "$(git branch --show-current)" --limit 3` then `gh run view <id> --log-failed`
- Fix within PR scope, push, and re-watch.
- If failures are **unrelated** to the dependency (flaky infra, broken default branch), merge base into the branch once:

```bash
git fetch origin
git merge origin/$DEFAULT
# resolve conflicts if any, run tests, push
git push origin HEAD
gh pr checks <number> --watch
```

If CI still fails after reasonable fixes, **skip this PR** and document the blocker.

### 3g. Merge

When local tests pass and required CI checks are green:

```bash
gh pr merge <number> --merge --delete-branch
```

Detect repo merge style from recent history when `--merge` is wrong:

```bash
gh pr merge <number> --squash --delete-branch   # squash-merge repos
gh pr merge <number> --rebase --delete-branch   # rebase-merge repos
```

Prefer the strategy used by recent merged PRs in the repo.

Return to the default branch before the next PR:

```bash
git checkout "$DEFAULT"
git pull origin "$DEFAULT"
```

Re-list open Dependabot PRs and continue.

## 4. Final Report

Return a structured summary:

```markdown
## Dependabot merge summary

**Repository:** <owner/repo>
**Default branch:** <branch>

### Merged (N)
- #123 — bump lodash 4.17.20 → 4.17.21 (patch, no code changes)
- #124 — bump axios 0.x → 1.x (major, fixed interceptors API)

### Skipped (M)
- #125 — bump webpack 4 → 5 — reason: requires config rewrite beyond PR scope

### Blockers
- <anything needing user decision>
```

## Integration with Babysit

When a PR needs comment triage or repeated CI fixes, apply the **babysit** skill on that single PR before merge: resolve conflicts, address valid review comments, fix CI — still within PR scope.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Merge with failing CI or tests | Fix or skip |
| Roll back the version bump to go green | Fix forward on the PR branch |
| Batch-merge without re-listing PRs | Re-list after each merge |
| Parallel checkouts of multiple Dependabot branches | One PR at a time |
| Major refactors bundled with a dep bump | Minimal migration-only changes |
| Force-push to default branch | Push only to the Dependabot branch |
| Ignore security PRs | Prioritize them first |

## Additional Resources

- Command reference and examples: [examples.md](examples.md)
