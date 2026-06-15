---
name: github-publish
description: >-
  Track all code changes in git and publish to GitHub using the GitHub CLI.
  Creates public repositories by default, commits work to a branch, opens a
  draft PR, and completes PR checklist items. Use when starting or finishing
  work on a project, when the user asks to publish or push code, create a
  repository, open a PR, or track changes with git and GitHub.
---

# GitHub Publish

## Core Rules

1. **All changes should be tracked in git** — no uncommitted deliverables at the end of a task.
2. **Repositories should be published to GitHub publicly unless otherwise specified** — use `--private` only when the user explicitly asks.
3. **Use the GitHub CLI (`gh`)** to create and interact with repositories, pull requests, and related GitHub resources.
4. **When you finish doing something you're told to do**, commit and push changes to a new branch, open a draft PR, and complete any todo items on the PR page.

These rules apply to every task unless the user explicitly opts out (e.g. "don't commit", "keep this local", "private repo").

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
gh repo create <repo-name> --public --source=. --remote=origin
```

Use the current directory name for `<repo-name>` unless the user specifies otherwise. Add a `.gitignore` appropriate to the stack before the first commit.

### Existing git repo, no remote

```bash
gh repo create <repo-name> --public --source=. --remote=origin --push
```

### Existing remote

Confirm the remote URL and visibility:

```bash
git remote -v
gh repo view --json visibility,url
```

Do not recreate the repo if a valid `origin` already points to GitHub.

### Private repos

Only when explicitly requested:

```bash
gh repo create <repo-name> --private --source=. --remote=origin
```

## During Work

- Commit logical units of progress when it helps recovery, but **always** leave a clean final commit on the feature branch before opening the PR.
- Never commit secrets (`.env`, credentials, tokens). Warn the user if they ask to commit sensitive files.
- Never update git config, skip hooks, force-push to `main`/`master`, or run destructive git commands unless the user explicitly requests them.

## Finish Workflow

When the assigned task is complete, run this sequence. Do not skip steps unless the user said not to push or open a PR.

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

### 2. Create a feature branch

Branch from the repo's default branch (`main` unless the project uses another):

```bash
git fetch origin
git checkout -b <type>/<short-description> origin/main
```

Use a descriptive prefix: `feat/`, `fix/`, `docs/`, `chore/`. Example: `feat/add-github-publish-skill`.

If work already exists on another branch, keep that branch or rename it — do not pile unrelated changes onto `main`.

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

### 6. Complete PR todo items

After creating the PR, load the PR page content and resolve every checklist item you can justify from the work performed:

```bash
gh pr view --json body,url,number
```

For each `- [ ]` item in the PR body:

- **Done** — change to `- [x]` with a brief note if helpful.
- **Not applicable** — check it off with `(n/a)` and one-line rationale.
- **Blocked / needs user** — leave unchecked and call it out in your final message to the user.

Update the body:

```bash
gh pr edit <number> --body-file /tmp/pr-body.md
```

Also complete any GitHub-side todos visible via `gh pr view` (linked issues, project tasks) when you have enough context; otherwise report what remains.

Return the PR URL to the user when finished.

## Agent Checklist

Copy and track while finishing a task:

```
Publish workflow:
- [ ] All deliverables tracked in git (nothing important left untracked)
- [ ] Remote exists on GitHub (public unless user specified private)
- [ ] Feature branch created (not committing directly to main)
- [ ] Changes committed with a clear message
- [ ] Branch pushed to origin
- [ ] Draft PR opened with summary and test plan
- [ ] PR checklist todos reviewed and updated
- [ ] PR URL shared with the user
```

## Common Commands

| Goal | Command |
|------|---------|
| Create public repo from cwd | `gh repo create NAME --public --source=. --remote=origin` |
| Open draft PR | `gh pr create --draft --title "..." --body "..."` |
| View PR | `gh pr view --web` or `gh pr view --json body,url` |
| Edit PR body | `gh pr edit --body-file file.md` |
| Check CI | `gh pr checks` |
| Repo visibility | `gh repo view --json visibility` |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Leaving completed work uncommitted | Commit on a feature branch before reporting done |
| Pushing directly to `main` | Branch → commit → push → draft PR |
| Creating private repos by default | `--public` unless user says private |
| Using web UI when `gh` suffices | Prefer `gh` for repos, PRs, checks |
| Empty or placeholder PR bodies | Summary + test plan; follow repo PR template |
| Leaving PR checklists untouched | Mark items done, n/a, or explain blockers |
| `git push --force` to shared branches | Push feature branches only; warn before any force push |

## Additional Resources

- Copy-paste command sequences: [examples.md](examples.md)
