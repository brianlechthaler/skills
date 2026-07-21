---
name: github-prune-branches
description: >-
  Safely prune old local and remote git branches that are fully merged or whose
  PRs are closed/merged. Protects the default branch, the current branch, and
  protected patterns; dry-runs before deleting. Use when the user asks to prune
  branches, clean up old branches, delete stale branches, tidy remotes, or
  remove merged feature branches.
---

# GitHub Prune Branches

Safely remove stale local and remote branches without deleting work that still
matters. Prefer evidence (merged into default, closed/merged PR) over age alone.

Complements [github-merge-all](../github-merge-all/SKILL.md) (lands open PRs)
and [github-publish](../github-publish/SKILL.md) (creates feature branches).
This skill only **deletes** branches after safety checks.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| User asks to prune, clean up, or delete old/stale/merged branches | Merging open PRs — use [github-merge-all](../github-merge-all/SKILL.md) |
| Local branches left after merged PRs | Force-deleting unmerged work without confirmation |
| Remote branches whose PRs are merged or closed | Rewriting history or force-pushing the default branch |
| Stale remote-tracking refs after remote deletes | Changing branch protection rules in repo settings |

## Core Rules

1. **Never delete protected refs** — default branch, current checkout, and protected name patterns stay untouched.
2. **Dry-run first** — list every candidate and the reason it qualifies before any delete.
3. **Merged or closed-PR only by default** — auto-delete only when the branch is fully merged into the default branch **or** its associated PR is `MERGED`/`CLOSED` with no unique unmerged commits the user cares about.
4. **Unmerged = ask** — branches with commits not in `origin/$DEFAULT` require explicit user approval (or an explicit "delete unmerged too" request).
5. **Use `gh` + git** — discover PR state with `gh`; delete remotes with `git push origin --delete` or `gh api`; delete locals with `git branch -d` (prefer `-d` over `-D`).
6. **Fetch and prune tracking refs** — end with `git fetch --prune` so gone remotes disappear from local tracking.

## Prerequisites

```bash
gh auth status
git fetch origin --prune
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
CURRENT=$(git branch --show-current)
```

If `gh` is not authenticated, run `gh auth login` and stop until the user completes it.

## Protected Branches

Never delete a branch that matches any of these:

| Protection | Examples |
|------------|----------|
| Default branch | `main`, `master` (whatever `$DEFAULT` is) |
| Current checkout | `$CURRENT` |
| Common long-lived names | `develop`, `development`, `staging`, `production`, `release`, `releases` |
| Release / hotfix prefixes | `release/*`, `releases/*`, `hotfix/*` |
| Repo branch protection rules | Names returned by protection APIs when available |

Optional extra keep-list: any patterns the user names (e.g. "keep `cursor/*`").

```bash
# Branch protection names (best-effort; may require admin)
gh api "repos/{owner}/{repo}/branches" --paginate \
  -q '.[] | select(.protected == true) | .name'
```

## Workflow Checklist

Copy and track:

```
Prune branches:
- [ ] Fetched origin with --prune; default and current branch identified
- [ ] Protected set built (default, current, long-lived, user keep-list)
- [ ] Candidates listed with reason (merged / closed PR / stale age)
- [ ] Dry-run shown to user (or logged before delete when user said "just prune")
- [ ] Safe deletes executed (remote then local)
- [ ] Unmerged leftovers reported (not deleted unless approved)
- [ ] Final fetch --prune and summary
```

## 1. Discover Branches

### Local

```bash
git branch --format='%(refname:short)'
git branch --merged "origin/$DEFAULT" --format='%(refname:short)'
git branch --no-merged "origin/$DEFAULT" --format='%(refname:short)'
```

### Remote

```bash
git branch -r --format='%(refname:short)' | sed 's|^origin/||' | grep -v '^HEAD$'
```

### PR association (per branch)

```bash
gh pr list --state all --head "<branch>" \
  --json number,state,mergedAt,closedAt,url,title \
  --limit 5
```

Or bulk:

```bash
gh pr list --state all --limit 200 \
  --json number,state,headRefName,mergedAt,closedAt,url,title
```

## 2. Classify Candidates

For each local or remote branch **not** in the protected set:

| Class | Condition | Default action |
|-------|-----------|----------------|
| **Safe — merged** | `git merge-base --is-ancestor <branch> origin/$DEFAULT` succeeds (fully contained) | Delete |
| **Safe — PR merged/closed** | Latest PR for head is `MERGED` or `CLOSED`, and branch has no commits beyond `origin/$DEFAULT` worth keeping | Delete |
| **Stale remote after merge** | PR merged with `--delete-branch` already removed remote; only local leftover remains | Delete local with `-d` |
| **Unmerged / open PR** | Has unique commits, or open/draft PR still targets the branch | **Keep**; report only |
| **Unknown age-only** | Old by date but unmerged and no PR | **Keep** unless user opts in |

### Age filter (optional)

When the user specifies a threshold (e.g. "older than 30 days"), apply it as an **additional** filter on top of safety class — never as the sole reason to delete unmerged work:

```bash
# Last commit date on a branch (ISO)
git log -1 --format='%cI' "<branch>"
# Or for remote:
git log -1 --format='%cI' "origin/<branch>"
```

Default when unspecified: no age gate — rely on merged / PR-closed evidence.

## 3. Dry-Run Report

Before deleting, present a table:

```markdown
## Branch prune dry-run

**Default:** <default> · **Current:** <current> · **Protected:** <list>

### Will delete (N)
| Branch | Scope | Reason |
|--------|-------|--------|
| feat/foo | local+remote | merged into main; PR #12 MERGED |
| cursor/bar-1234 | local | ancestor of origin/main |

### Will keep (M)
| Branch | Reason |
|--------|--------|
| feat/wip | open PR #44 |
| experiment/x | unmerged commits; no PR |

### Blocked / protected
| Branch | Reason |
|--------|--------|
| main | default branch |
| develop | long-lived name |
```

When the user already said to prune without review (e.g. "prune merged branches now"), still compute this list, delete only the **Will delete** set, and include the same table in the final summary.

## 4. Delete Safely

Order: **remote first**, then **local**, so locals can track the update.

### Remote

```bash
git push origin --delete <branch>
```

If the remote is already gone (`remote ref does not exist`), continue — treat as success for that ref.

### Local (merged)

```bash
git branch -d <branch>
```

Use `git branch -D` **only** when:

- The user explicitly approved deleting that unmerged branch, **or**
- The branch tip is gone remotely, the PR is MERGED/CLOSED, and `-d` refuses solely because of a squash-merge (tip not an ancestor). Confirm with:

```bash
gh pr list --state merged --head "<branch>" --limit 1
git rev-list --count "origin/$DEFAULT..<branch>"   # unique commits
```

For squash-merged branches: if the PR is `MERGED` and the user asked to prune merged branches, `-D` is acceptable after documenting squash-merge as the reason.

### Tracking cleanup

```bash
git fetch origin --prune
git remote prune origin
```

## 5. Final Report

```markdown
## Branch prune summary

**Repository:** <owner/repo>
**Default branch:** <branch>

### Deleted (N)
- `feat/foo` (remote+local) — PR #12 merged
- `cursor/old-8697` (local) — fully merged

### Kept (M)
- `feat/wip` — open PR #44
- `experiment/x` — unmerged; needs decision

### Errors
- `feat/locked` — permission denied on remote delete
```

## Integration with Other Skills

| Situation | Skill |
|-----------|-------|
| Open PRs still need landing before prune | [github-merge-all](../github-merge-all/SKILL.md) |
| Finish work and delete branch via merge | [github-publish](../github-publish/SKILL.md) (`gh pr merge --delete-branch`) |
| CI stuck on a stale branch tip | [ci-debug](../ci-debug/SKILL.md) |

Typical sequence: merge-all (optional) → prune branches → confirm clean `git branch -a`.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| `git branch -D` on everything older than N days | Classify merged/PR-closed first; age is optional filter only |
| Deleting `main` / `$DEFAULT` / current branch | Maintain an explicit protected set |
| Deleting a branch with an open PR | Keep and list under "Will keep" |
| Bulk remote delete without dry-run | Always build the candidate table first |
| Leaving stale `origin/*` tracking refs | `git fetch --prune` at the end |
| Assuming squash-merged tips are unmerged forever | Check PR `MERGED` state; then `-D` with documented reason |
| Force-push or `--force` delete on protected branches | Stop and report; never override protection |

## Additional Resources

- Command recipes: [examples.md](examples.md)
