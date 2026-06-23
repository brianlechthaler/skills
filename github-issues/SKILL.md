---
name: github-issues
description: >-
  Find open GitHub issues in the current repository, triage and prioritize them,
  implement one fix per issue on its own feature branch with a draft PR, comment
  on each issue with progress, and close issues when work is complete. Follows
  the github-publish workflow for branches, PRs, tests, CI, and merge approval.
  Use when the user asks to fix open issues, clear the issue backlog, work
  through GitHub issues, or address all open issues in the repo.
---

# GitHub Issues

Work through every open issue in the current repository: triage, implement, publish one PR per issue, keep issues updated, close when done.

## Core Rules

1. **Use `gh` for all GitHub operations** — list issues, comment, link PRs, close issues, open PRs, watch CI.
2. **One issue → one branch → one PR** — never bundle multiple unrelated issues into a single PR.
3. **Comment on each issue** as work progresses (starting, blocked, PR opened, merged).
4. **Close each issue** when its fix is merged or when the issue is resolved another way (duplicate, already fixed, won't fix with rationale).
5. **Never commit directly to the default branch** — follow [github-publish](../github-publish/SKILL.md) for every deliverable.
6. **Ask for merge approval** before merging each issue PR — do not merge without explicit user approval.
7. **One issue at a time** — finish (merge approved + issue closed) or explicitly defer before starting the next. Re-list issues after each merge; priorities and duplicates change.
8. **Follow project gates** — run [test](../test/SKILL.md) and [lint](../lint/SKILL.md) when changing code; use [docker](../docker/SKILL.md) when the project runs tooling in containers.

## Prerequisites

```bash
gh auth status
git remote -v
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
```

If `gh` is not authenticated, run `gh auth login` and stop until the user completes it.

## Workflow Checklist

Copy and track for the full backlog run:

```
GitHub issues workflow:
- [ ] Open issues discovered and triaged
- [ ] Duplicates merged/closed, already-fixed and blocked issues handled
- [ ] Priority order agreed (or inferred from labels/age)
- [ ] Per issue: commented → branched → implemented → draft PR → tests → CI → merge approval → closed
- [ ] Final summary shared (closed, deferred, blockers)
```

## 1. Discover Open Issues

List all open issues with metadata:

```bash
gh issue list --state open \
  --json number,title,labels,assignees,createdAt,updatedAt,author,body,url,milestone \
  --limit 200
```

If the repo is large, also search by label or assignee when the user scopes the work:

```bash
gh issue list --state open --label "bug" --json number,title,labels,url
gh issue list --state open --assignee "@me" --json number,title,url
```

Record for each issue: number, title, labels, assignees, URL, age, and a one-line summary of the ask.

When **zero** open issues, report that and stop — do not invent work.

## 2. Triage and Prioritize

Before implementing, classify every open issue:

| Classification | Action |
|----------------|--------|
| **Duplicate** | Comment linking the canonical issue; close as duplicate |
| **Already fixed** | Verify on `origin/$DEFAULT`; comment with evidence; close |
| **Needs clarification** | Comment with specific questions; add `question` label if available; **skip** until answered |
| **Out of scope** | Comment explaining why; close or leave for maintainer per user intent |
| **Actionable** | Queue for implementation |

### Duplicate detection

```bash
# Search for similar titles or bodies
gh issue list --state all --search "in:title <keywords>" --json number,title,state,url
```

When two issues describe the same work, keep the older or more detailed issue as canonical. Close the other:

```bash
gh issue comment <dup-number> --body "Duplicate of #<canonical>. Closing in favor of the original."
gh issue close <dup-number> --reason "not planned"   # or omit --reason; prefer linking in comment
```

Reference the canonical issue in the comment body so GitHub cross-links.

### Already fixed

Check whether `origin/$DEFAULT` already contains the fix:

```bash
git fetch origin
git log origin/$DEFAULT --oneline -20
# Search codebase for symbols or behavior described in the issue
```

If fixed on the default branch without a linked PR:

```bash
gh issue comment <number> --body "Verified fixed on \`$DEFAULT\` in <commit-sha or version>. Closing."
gh issue close <number>
```

### Needs clarification

Post a comment with numbered questions. Do not open a PR until the reporter or user answers:

```bash
gh issue comment <number> --body "$(cat <<'EOF'
Thanks for filing this. Before I can implement a fix, I need:

1. <specific question>
2. <specific question>

I'll pick this up once clarified.
EOF
)"
```

Track skipped issues in the final summary.

### Prioritization

Default order unless the user specifies otherwise:

| Priority | Signal | Rationale |
|----------|--------|-----------|
| 1 | `priority: critical`, `security`, `bug` + production impact | User-visible breakage or risk |
| 2 | `bug` | Correctness |
| 3 | `enhancement`, `feature` | New capability |
| 4 | `documentation`, `chore`, `good first issue` | Lower urgency |

Within the same tier, process **oldest first** (`createdAt`). Respect explicit user ordering ("fix #42 first").

## 3. Process Each Issue

For each actionable issue in priority order:

### 3a. Announce work

```bash
gh issue comment <number> --body "Starting work on this — branch and draft PR incoming."
```

Optional: assign yourself when appropriate:

```bash
gh issue edit <number> --add-assignee "@me"
```

### 3b. Create a feature branch

Branch from the latest default branch. Name after the issue:

```bash
git fetch origin
git checkout "$DEFAULT"
git pull origin "$DEFAULT"
git checkout -b fix/issue-<number>-<short-slug>
```

Slug examples: `fix/issue-42-null-session`, `feat/issue-15-export-csv`. Use `fix/`, `feat/`, or `docs/` prefixes per [github-publish](../github-publish/SKILL.md).

Ensure no unrelated uncommitted work rides on this branch.

### 3c. Implement the fix

- Scope changes to **this issue only** — no drive-by refactors.
- Read the issue body, comments, and linked PRs for acceptance criteria.
- Follow [test](../test/SKILL.md) and [lint](../lint/SKILL.md) for code changes.

Post a progress comment if implementation spans multiple steps or hits a blocker:

```bash
gh issue comment <number> --body "Update: <what is done / what is blocked and why>."
```

### 3d. Publish via github-publish

Read and follow [github-publish](../github-publish/SKILL.md) **Finish Workflow** for this branch:

1. Commit with a clear message referencing the issue
2. Push the branch
3. Open a **draft** PR linked to the issue
4. Complete every PR checklist item
5. Run local tests
6. `gh pr checks --watch` until CI is green
7. Ask the user for merge approval — **do not merge** without it

**PR title:** imperative, scoped to the issue (e.g. `Fix null session handling (#42)`).

**PR body** must include `Fixes #<number>` or `Closes #<number>` so GitHub auto-closes the issue on merge:

```bash
gh pr create --draft --title "Fix null session handling (#42)" --body "$(cat <<'EOF'
## Summary
- <what changed and why>

Fixes #42

## Test plan
- [ ] <verification step>
- [ ] Local tests pass
- [ ] CI passes

EOF
)"
```

If a PR already exists for this issue branch, update it instead of creating a duplicate:

```bash
gh pr list --head fix/issue-42-null-session --json number,url
```

Comment on the issue when the PR is open:

```bash
gh issue comment 42 --body "Draft PR: <pr-url>"
```

### 3e. Merge and close

After **explicit user approval**:

```bash
gh pr ready <number>    # if still draft
gh pr merge <number> --merge --delete-branch   # or --squash / --rebase per repo convention
```

GitHub closes the linked issue automatically when the PR body contains `Fixes #N` / `Closes #N`.

If the issue was resolved without merge (user asked to close manually):

```bash
gh issue close <number> --comment "Resolved by <pr-url>."
```

Return to the default branch before the next issue:

```bash
git checkout "$DEFAULT"
git pull origin "$DEFAULT"
```

Re-list open issues and continue.

## 4. Edge Cases

| Situation | What to do |
|-----------|------------|
| Issue has an open PR already | Review that PR; continue or supersede it — do not open a second PR for the same fix |
| Issue spans multiple repos | Comment that it is out of scope for this repo; close or defer |
| Fix requires breaking change | Comment on the issue; ask user before proceeding |
| CI fails on unrelated default branch | Merge `origin/$DEFAULT` into the issue branch once; re-test |
| User says "fix all issues" | Process sequentially; summarize after each merge; do not batch into one PR |
| Issue is a question, not a task | Answer in a comment; close if resolved, or leave open |
| Dependabot / automated issues | Use [dependabot-merge](../dependabot-merge/SKILL.md) for dependency PRs; use this skill for standard issues |

## 5. Final Report

Return a structured summary:

```markdown
## GitHub issues summary

**Repository:** <owner/repo>
**Default branch:** <branch>

### Closed (N)
- #42 — <title> — PR: <url>
- #15 — duplicate of #12 — closed without PR

### Deferred (M)
- #8 — needs clarification — waiting on reporter

### Skipped (K)
- #3 — out of scope — <reason>

### Blockers
- <anything needing user decision>
```

## Integration with Other Skills

| Skill | When |
|-------|------|
| [github-publish](../github-publish/SKILL.md) | Every issue PR — branches, draft PRs, checklist, CI, merge approval |
| [babysit](~/.cursor/skills-cursor/babysit/SKILL.md) | PR has review comments or repeated CI failures before merge |
| [orchestrate](../orchestrate/SKILL.md) | Single issue is large enough to parallelize explore/implement phases |
| [dependabot-merge](../dependabot-merge/SKILL.md) | Backlog is dependency PRs, not standard issues |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| One mega PR for many issues | One branch + one PR per issue |
| Silent work with no issue comments | Comment at start, PR link, and blockers |
| Merge without user approval | Ask after local + CI green |
| Close issues before fix is merged | Use `Fixes #N` in PR or close with explanation |
| Parallel branches for multiple issues | One issue at a time on default branch |
| Ignoring duplicates | Close duplicates with link to canonical issue |
| Implementing unclear requirements | Ask in issue comments first |
| Committing to default branch | Feature branch + PR per github-publish |

## Additional Resources

- Command reference and examples: [examples.md](examples.md)
