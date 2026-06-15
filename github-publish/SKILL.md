---
name: github-publish
description: >-
  Track all code changes in git and publish to GitHub using the GitHub CLI.
  Creates public repositories by default, commits work to a branch based on the
  default branch, opens a draft PR, completes all PR checklist items, waits for
  local and CI tests to pass, then asks for approval before merging. Use when
  starting or finishing work on a project, when the user asks to publish or push
  code, create a repository, open a PR, or track changes with git and GitHub.
---

# GitHub Publish

## Core Rules

1. **All changes should be tracked in git** — no uncommitted deliverables at the end of a task.
2. **Repositories should be published to GitHub publicly unless otherwise specified** — use `--private` only when the user explicitly asks.
3. **Use the GitHub CLI (`gh`)** to create and interact with repositories, pull requests, and related GitHub resources.
4. **Never commit directly to the default branch** — all deliverables live on a feature branch named after the changes and based on the default branch. The **only** exception is bootstrapping an empty default branch when the remote has none yet (see **Bootstrap Default Branch**).
5. **When you finish doing something you're told to do**, commit and push to that feature branch, open a draft PR, complete every PR todo item, run local and CI tests, then ask the user for approval before merging.

These rules apply to every task unless the user explicitly opts out (e.g. "don't commit", "keep this local", "private repo", "don't merge").

## Prerequisites

Verify `gh` is available and authenticated before creating remotes or PRs:

```bash
gh auth status
```

If not authenticated, run `gh auth login` and ask the user to complete the flow. Do not skip publishing because auth is missing — surface the blocker and retry after login.

## Repository Setup

Run at the start of work when the directory is not yet on GitHub.

### New project (no git yet)

```bash
git init
# Add a .gitignore appropriate to the stack (no project commit yet)
gh repo create <repo-name> --public --source=. --remote=origin
```

Use the current directory name for `<repo-name>` unless the user specifies otherwise. Do **not** push project commits to the default branch — bootstrap an empty default branch first (see **Bootstrap Default Branch**), then put all work on a feature branch and open a PR.

### Existing git repo, no remote

```bash
gh repo create <repo-name> --public --source=. --remote=origin
```

Do **not** use `--push` here unless the remote default branch already exists and matches your intended base. After adding the remote, bootstrap the default branch if missing, then push work from a feature branch via PR.

### Existing remote

Confirm the remote URL and visibility:

```bash
git remote -v
gh repo view --json visibility,url
```

Do not recreate the repo if a valid `origin` already points to GitHub.

### Bootstrap Default Branch

When the GitHub repository has **no default branch yet** (common right after `gh repo create` on an empty repo), create `main` (or the repo's configured default) with a single **empty** commit, push it, then do all real work on a feature branch merged via PR. That keeps every project commit on the default branch behind a PR — the empty bootstrap is the only direct push to the default branch, because GitHub requires at least one branch before PRs can target it.

**Detect a missing remote default branch:**

```bash
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || echo main)
# defaultBranchRef is null on a brand-new empty repo; fall back to main
if [ "$DEFAULT" = "null" ] || [ -z "$DEFAULT" ]; then DEFAULT=main; fi

if ! git rev-parse --verify "origin/$DEFAULT" >/dev/null 2>&1; then
  NEEDS_BOOTSTRAP=1
fi
```

**Bootstrap empty default branch** (only when `NEEDS_BOOTSTRAP=1`):

```bash
# Stash or keep uncommitted work aside — do not include it in the bootstrap commit
git stash push -u -m "publish-work"   # when you have uncommitted changes

git checkout --orphan "$DEFAULT"
git reset --hard
git commit --allow-empty -m "Initial commit"
git push -u origin "$DEFAULT"

git checkout -b <type>/<short-description>
git stash pop   # when you stashed above
```

Rules for bootstrap:

- The bootstrap commit must be **empty** (`git commit --allow-empty`) — no project files on the default branch.
- Push **only** this empty commit directly to the default branch; every later commit reaches the default branch through a merged PR.
- After bootstrap, create the feature branch from `origin/$DEFAULT` and commit all deliverables there.
- If local commits already exist on the wrong branch before bootstrap, move them to the feature branch after bootstrap (stash, cherry-pick, or new branch from `origin/$DEFAULT`) — never rewrite the bootstrap commit on the remote.

### Private repos

Only when explicitly requested:

```bash
gh repo create <repo-name> --private --source=. --remote=origin
```

## During Work

- Commit logical units of progress when it helps recovery, but **always** leave a clean final commit on the feature branch before opening the PR.
- Never commit secrets (`.env`, credentials, tokens). Warn the user if they ask to commit sensitive files.
- Never update git config, skip hooks, force-push to `main`/`master`, or run destructive git commands unless the user explicitly requests them.

## Feature Branch Rules

Before committing or opening a PR, put all changes on the right branch.

### 1. Resolve the default branch

```bash
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
```

Fall back to `main` only when `gh` is unavailable and `git symbolic-ref refs/remotes/origin/HEAD` does not resolve.

If `origin/$DEFAULT` does not exist, run **Bootstrap Default Branch** before creating the feature branch.

### 2. Name the branch after the changes

Use a descriptive prefix and short slug derived from the work:

- `feat/add-github-publish-skill`
- `fix/handle-null-session`
- `docs/update-readme`

Prefixes: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`.

### 3. Place changes on a branch based on the default branch

Check the current branch:

```bash
CURRENT=$(git branch --show-current)
```

| Situation | Action |
|-----------|--------|
| Remote default branch missing | Bootstrap empty `origin/$DEFAULT` first, then create feature branch |
| On the default branch (with or without uncommitted changes) | Create a new branch from `origin/$DEFAULT`, move work there, commit |
| On a feature branch that matches the work and is based on current `origin/$DEFAULT` | Keep the branch; rebase onto `origin/$DEFAULT` if behind |
| On a feature branch with the wrong name, wrong base, or unrelated history | Create `origin/$DEFAULT`-based branch with the correct name; move only this task's commits or uncommitted changes there — do not pile unrelated work onto one branch |
| Branch already exists on the remote with an open PR for the same work | Continue on that branch instead of creating a duplicate |

**Create a new branch from the default branch and move work:**

```bash
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)

# Uncommitted changes on default or wrong branch:
git stash push -u -m "publish-work"
git checkout -b <type>/<short-description> origin/$DEFAULT
git stash pop

# Commits on wrong branch (same task only):
git checkout -b <type>/<short-description> origin/$DEFAULT
git cherry-pick <first-commit>^..<last-commit>
```

Do not use destructive history rewrites (`reset --hard`, force-push) without explicit user approval. Prefer stash, cherry-pick, or a new branch from `origin/$DEFAULT`.

## Finish Workflow

When the assigned task is complete, run this sequence. Do not skip steps unless the user said not to push, open a PR, or merge.

### 1. Inspect state

Run in parallel:

```bash
git status
git diff
git diff --staged
git log --oneline -5
```

Check whether the branch tracks a remote and is up to date:

```bash
git status -sb
```

### 2. Ensure the feature branch

If `origin/$DEFAULT` does not exist, run **Bootstrap Default Branch** first.

Follow **Feature Branch Rules** above. Confirm:

- Current branch is **not** the default branch
- Branch name reflects the changes made
- Branch is based on the latest `origin/$DEFAULT` (rebase if needed and safe)

```bash
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git rebase origin/$DEFAULT   # when behind and no conflicts expected
```

### 3. Stage and commit

```bash
git add <relevant-files>
git commit -m "$(cat <<'EOF'
Concise summary of why, not just what.

EOF
)"
```

Match the repository's existing commit message style when `git log` shows a clear pattern.

### 4. Push the branch

```bash
git push -u origin HEAD
```

Request `git_write` and network permissions when the environment requires them.

### 5. Open a draft PR

```bash
gh pr create --draft --title "<Title>" --body "$(cat <<'EOF'
## Summary
- <what changed and why>

## Test plan
- [ ] <verification step>
- [ ] <verification step>

EOF
)"
```

Use a clear title (imperative, under ~72 chars). The summary should explain intent; the test plan should list concrete checks.

If the repo has a pull request template (`.github/pull_request_template.md` or `PULL_REQUEST_TEMPLATE.md`), read it and follow its structure instead of the generic body above.

If a PR already exists for this branch, update it instead of creating a duplicate:

```bash
gh pr view --json number,url
```

### 6. Complete all PR todo items

**Every checklist item must be resolved before you report the task done.** Do not leave `- [ ]` items open unless the user must perform them manually — and call those out explicitly.

After creating or updating the PR:

```bash
gh pr view --json body,url,number
```

For each `- [ ]` item in the PR body:

- **Done** — change to `- [x]` with a brief note if helpful.
- **Not applicable** — check it off with `(n/a)` and one-line rationale.
- **Needs user action** — leave unchecked, list in your final message, and do not proceed to merge approval until the user completes them or agrees to defer.

Update the body:

```bash
gh pr edit <number> --body-file /tmp/pr-body.md
```

Also complete any GitHub-side todos visible via `gh pr view` (linked issues, project tasks) when you have enough context.

Re-read the PR body after editing and confirm **zero** unjustified open checkboxes remain.

### 7. Run local tests

Run the project's standard test, lint, and build commands (discover from `package.json`, `Makefile`, `README`, or CI workflows). Fix failures within the PR's scope before continuing.

Do not mark test-plan items complete until the corresponding commands have actually been run successfully.

### 8. Wait for CI

```bash
gh pr checks --watch
```

If CI fails, fix issues caused by this PR's changes and push again. Re-run `gh pr checks --watch` until all required checks pass or you hit a blocker outside this PR's scope (report the blocker instead of merging).

When CI is green, update any PR checklist items that depend on CI (e.g. `- [x] CI passes`).

### 9. Ask for merge approval

Only after **all** of the following are true:

- Every PR todo item is checked off (or explicitly deferred by the user)
- Local tests pass
- Required CI checks pass

Ask the user clearly, for example:

> All local tests and CI checks passed. PR: \<url\>. Approve merge into \<default-branch\>?

Wait for explicit approval. Do **not** merge on your own.

If the user approves:

```bash
gh pr ready    # mark ready for review if still a draft
gh pr merge --merge --delete-branch
```

Use `--squash` or `--rebase` when the repo's conventions or the user prefer those strategies. Do not force-push to the default branch.

If the user declines or does not respond, leave the PR open and return the URL.

### 10. Report back

Return the PR URL, branch name, test/CI status, and whether the PR was merged or is awaiting approval.

## Agent Checklist

Copy and track while finishing a task:

```
Publish workflow:
- [ ] All deliverables tracked in git (nothing important left untracked)
- [ ] Remote exists on GitHub (public unless user specified private)
- [ ] Default branch identified (bootstrapped with empty commit if remote had none)
- [ ] Feature branch named after changes and based on default branch (not committing deliverables to main)
- [ ] Changes committed with a clear message
- [ ] Branch pushed to origin
- [ ] Draft PR opened (or existing PR updated) with summary and test plan
- [ ] All PR checklist todos completed (none left open without user deferral)
- [ ] Local tests pass
- [ ] CI checks pass
- [ ] User asked for merge approval
- [ ] PR merged only after explicit user approval
- [ ] PR URL and final status shared with the user
```

## Common Commands

| Goal | Command |
|------|---------|
| Default branch name | `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` |
| Create public repo from cwd | `gh repo create NAME --public --source=. --remote=origin` |
| Bootstrap empty default branch | `git checkout --orphan main && git commit --allow-empty -m "Initial commit" && git push -u origin main` |
| Branch from default | `git checkout -b feat/name origin/$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)` |
| Open draft PR | `gh pr create --draft --title "..." --body "..."` |
| View PR | `gh pr view --web` or `gh pr view --json body,url` |
| Edit PR body | `gh pr edit --body-file file.md` |
| Watch CI | `gh pr checks --watch` |
| Mark PR ready | `gh pr ready` |
| Merge PR | `gh pr merge --merge --delete-branch` |
| Repo visibility | `gh repo view --json visibility` |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Leaving completed work uncommitted | Commit on a feature branch before reporting done |
| Pushing project commits directly to `main` | Bootstrap empty `main` once if missing; branch → commit → push → draft PR |
| Using `--push` on a new empty remote | Add remote without `--push`; bootstrap empty default branch, then feature-branch PR |
| Working on a misnamed or stale-base branch | Create/rename a branch from `origin/$DEFAULT` named after the changes |
| Creating private repos by default | `--public` unless user says private |
| Using web UI when `gh` suffices | Prefer `gh` for repos, PRs, checks |
| Empty or placeholder PR bodies | Summary + test plan; follow repo PR template |
| Leaving PR checklists with open items | Complete every item or get explicit user deferral |
| Merging without user approval | Ask after local + CI green; merge only on approval |
| `git push --force` to shared branches | Push feature branches only; warn before any force push |

## Additional Resources

- Copy-paste command sequences: [examples.md](examples.md)
