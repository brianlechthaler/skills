---
name: github-login
description: >-
  Check GitHub CLI login with gh auth status and ask the user to authenticate
  to GitHub only when they are not already logged in. Use before any gh command,
  when the user mentions github-login, gh auth, GitHub authentication, or
  logging into GitHub, and from other GitHub skills that need the CLI.
---

# GitHub Login

Confirm GitHub CLI authentication before any `gh` work.

Always check if the user is logged in and only if they are not logged in then you should ask the user to authenticate to github.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| Any `gh` command (repos, PRs, issues, releases, Actions) | Git-only work with no GitHub API / `gh` calls |
| Other GitHub skills ([github-publish](../github-publish/SKILL.md), [github-issues](../github-issues/SKILL.md), [github-release](../github-release/SKILL.md), [github-merge-all](../github-merge-all/SKILL.md), [github-prune-branches](../github-prune-branches/SKILL.md), [dependabot-merge](../dependabot-merge/SKILL.md), [ci-debug](../ci-debug/SKILL.md), [ci-optimize](../ci-optimize/SKILL.md)) | User explicitly opts out of GitHub CLI auth |
| User asks to log in, authenticate, or check `gh auth` | Installing the `gh` binary with no intent to use it yet |

## Workflow

```
GitHub login:
- [ ] `gh` is on PATH
- [ ] `gh auth status` ran (never skip)
- [ ] Logged in → continue; do not ask to authenticate
- [ ] Not logged in → ask the user to authenticate to GitHub, then complete login, then re-check status
```

1. **Ensure `gh` exists** — `gh --version`. If it fails, tell the user to install [GitHub CLI](https://cli.github.com/) and stop. Do not ask them to authenticate until `gh` can run.
2. **Always check login** — run `gh auth status`. Never assume logged in or logged out. Never start with `gh auth login`.
3. **Already logged in** (exit code 0) — continue the original task. Do not ask the user to authenticate to GitHub.
4. **Not logged in** — ask the user to authenticate to GitHub. After they agree, run `gh auth login` and stop until they finish the flow. Then run `gh auth status` again and continue only when it succeeds.

## Commands

Check (always first):

```bash
gh auth status
```

Ask the user to authenticate only when that check fails. Then:

```bash
gh auth login
gh auth status
```

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Run `gh auth login` before `gh auth status` | Always check login first |
| Ask the user to authenticate when already logged in | Continue silently after a successful status check |
| Skip the status check because login "probably" works | Always run `gh auth status` |
| Prompt for GitHub auth when `gh` is missing | Ask to install GitHub CLI first, then check login |

## Additional Resources

- Command examples: [examples.md](examples.md)
