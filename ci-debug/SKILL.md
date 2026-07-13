---
name: ci-debug
description: >-
  Debug GitHub Actions and CI pipeline failures — fetch logs, classify errors,
  reproduce locally, and optionally fix the underlying issue. Use when CI is
  failing, GitHub Actions checks are red, a workflow run failed, the user asks
  to debug or fix CI, investigate pipeline errors, or diagnose why tests or
  builds fail in GitHub Actions.
---

# CI Debug

Investigate **why CI failed**, reproduce the failure locally when possible, and optionally land a fix. Treat CI logs as the source of truth — do not guess from memory or assume local green means CI green.

For speeding up already-green pipelines, use [ci-optimize](../ci-optimize/SKILL.md). For authoring workflows from scratch, use [github-workflows](../github-workflows/SKILL.md).

## Fix Mode (decide first)

| User intent | Behavior after diagnosis |
|-------------|--------------------------|
| Default — "debug CI", "why is CI failing", "investigate the pipeline", etc. | Deliver root-cause analysis, then **ask** whether to apply fixes |
| Explicit fix — "debug and fix CI", "fix CI", "fix the failing checks", "make CI green", "repair the pipeline" | **Skip the prompt** — implement fixes immediately after diagnosis |

When fixing:

1. Fix the **root cause**, not symptoms (masking failures, skipping tests, loosening gates)
2. Reproduce locally with the **same commands CI runs** before pushing
3. Follow [test](../test/SKILL.md) and [lint](../lint/SKILL.md) for any code changes
4. Use [docker](../docker/SKILL.md) when the project runs tooling in containers
5. Push to the existing PR/feature branch; watch CI until green or blocked
6. Follow [github-publish](../github-publish/SKILL.md) when opening or updating PRs

When prompting (default), use AskQuestion when available:

- **Prompt**: "Apply fixes for the CI failure(s) identified?"
- **Options**: "Yes — fix all identified issues", "Yes — fix only blocking failures", "No — report only"

If AskQuestion is unavailable, ask conversationally with the same options.

## Prerequisites

```bash
gh auth status
git fetch origin
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
```

If `gh` is not authenticated, run `gh auth login` and stop until the user completes it.

Identify context:

```bash
# Current branch and recent commits
git branch --show-current
git log --oneline -5

# Workflows in this repo
ls -la .github/workflows/
gh workflow list
```

## Debug Workflow

Copy and track progress:

```
CI debug progress:
- [ ] Target identified (branch, PR, run ID, failing check name)
- [ ] Failed jobs/steps listed from run metadata
- [ ] Failure logs fetched and first root error isolated
- [ ] Failure classified (test, lint, build, container, workflow, infra, permissions)
- [ ] CI command reproduced locally (or documented why not)
- [ ] Root cause stated in one sentence
- [ ] Fix mode — prompt or apply fixes
- [ ] Fix pushed and CI re-run verified (when fixing)
```

Run steps **in order**. Do not propose fixes before reading the actual failure output.

## 1. Identify the failing run

### Current branch / open PR

```bash
BRANCH=$(git branch --show-current)

gh pr view --json number,title,url,statusCheckRollup,headRefName,baseRefName 2>/dev/null \
  || echo "No PR for current branch"

gh run list --branch "$BRANCH" --limit 10 \
  --json databaseId,displayTitle,conclusion,workflowName,createdAt,updatedAt,event,headSha

gh pr checks --watch   # when a PR exists and you are waiting after a push
```

Pick the **most recent failed run** on the commit under investigation (`headSha` on the PR or `HEAD` locally).

### Specific PR or run the user named

```bash
gh pr view <number> --json statusCheckRollup,headRefName,commits
gh run view <run-id> --json conclusion,jobs,workflowName,headBranch,headSha,url
```

Record:

| Field | Value |
|-------|-------|
| Run ID | |
| Workflow | |
| Branch / PR | |
| Commit SHA | |
| Failed job(s) | |
| Failed step(s) | |

## 2. Fetch failure logs

```bash
# Run summary and job list
gh run view <run-id> --json jobs --jq '.jobs[] | {name, conclusion, steps: [.steps[] | select(.conclusion=="failure") | .name]}'

# Failed-step logs only (start here)
gh run view <run-id> --log-failed

# Full logs when context is missing
gh run view <run-id> --log

# Open in browser for long logs
gh run view <run-id> --web
```

**Isolate the first actionable error** — scroll past cascading failures to the earliest non-zero exit, assertion failure, compile error, or permission denied. Quote the exact error lines in your report.

For matrix/sharded jobs, identify **which shard failed** and whether others passed (flake vs systematic failure).

## 3. Classify the failure

| Category | Signals | Typical fix location |
|----------|---------|----------------------|
| **Unit/integration test** | `FAIL`, assertion errors, pytest/jest/vitest/cargo test output | Application code or test code |
| **Lint / format** | eslint, ruff, clippy, prettier, golangci-lint violations | Source files; run fixers locally |
| **Type check** | tsc, mypy, pyright errors | Types or annotations |
| **Build / compile** | Missing module, syntax error, linker failure | Source, deps, or build config |
| **Dependency install** | `npm ci`, `pip install`, lockfile mismatch | Lockfiles, version pins, registry auth |
| **Container / Docker** | `docker build`, push to GHCR, 403 on packages | Dockerfile, build args, `packages: write` |
| **Workflow / YAML** | actionlint errors, invalid expression, missing input | `.github/workflows/*.yml` |
| **Permissions / secrets** | `403`, `Resource not accessible`, missing secret | Workflow `permissions`, repo secrets |
| **Timeout / OOM** | `The job was not started`, `Killed`, exceeded time limit | Optimize job, shard tests, raise timeout |
| **Flaky / infra** | Passes on retry, GitHub outage, rate limits | Re-run; document if persistent |
| **Environment drift** | Passes locally, fails in CI — version mismatch | Align Node/Python/Go version with workflow |

When multiple jobs fail, fix in **dependency order**: lint/typecheck before tests, build before container push, workflow syntax before anything runs.

## 4. Map CI to local commands

Read the failing workflow file and extract the exact commands:

```bash
# Example paths
cat .github/workflows/test.yml
cat .github/workflows/lint.yml
cat .github/workflows/container.yml
```

Build a **reproduction recipe** — the minimal local sequence that should fail the same way:

| CI step | Local equivalent |
|---------|------------------|
| `actions/setup-node` with `node-version: "20"` | `nvm use 20` or run in matching container |
| `npm ci` | `npm ci` (not `npm install`) |
| `npm test` | same flags as CI |
| `docker build` / `docker run ... npm test` | same Dockerfile and tags |
| `pytest -q` with env vars | export the same env vars locally |

If the [docker](../docker/SKILL.md) skill applies, reproduce **inside the container** CI uses.

When local reproduction fails differently:

- Match **OS** (CI is usually `ubuntu-latest`)
- Match **tool versions** exactly (check workflow `setup-*` steps)
- Match **env vars and secrets** — use `.env.example` or ask the user for required secrets
- Check **path filters** — CI may not have run the workflow you expect on docs-only changes

## 5. Diagnose root cause

State root cause clearly:

> **Root cause:** `<one sentence>`  
> **Evidence:** `<exact log lines or local repro output>`  
> **Scope:** `<files/workflows involved>`

Common patterns:

| Pattern | What to check |
|---------|---------------|
| "Works on my machine" | Version pins, missing system deps, uncommitted files |
| Lockfile out of sync | Regenerate lockfile with the same package manager CI uses |
| New test flakiness | Timing, network mocks, shared state — fix test, don't disable |
| GHCR 403 | `permissions.packages: write`, package linked to repo |
| `GITHUB_TOKEN` permissions | Fine-grained token defaults; add job-level `permissions` |
| Matrix partial failure | One shard only — read that shard's log |
| Merge conflict / stale branch | Rebase onto default; re-run CI |

Do **not** fix by disabling tests, lowering coverage thresholds, or `continue-on-error` unless the user explicitly accepts that tradeoff.

## 6. Apply fixes (fix mode)

### Code / test / config fixes

1. Change the minimum files required for the root cause
2. Run the **same local reproduction** until green
3. Follow [test](../test/SKILL.md) and [lint](../lint/SKILL.md) for changed code
4. Commit with a message that references the failure, e.g. `fix(ci): resolve lint errors in api module`

### Workflow fixes

When the bug is in `.github/workflows/`:

```bash
# Validate when available
actionlint .github/workflows/*.yml
```

Keep changes focused — fix the failing step, don't rewrite unrelated jobs. After editing, push and watch the specific workflow.

### Push and verify

```bash
git push origin HEAD

gh run list --branch "$(git branch --show-current)" --limit 3 \
  --json databaseId,conclusion,workflowName,createdAt

gh run watch <new-run-id>
gh pr checks --watch   # when on a PR
```

If CI still fails, return to step 2 with the new run ID — do not stack speculative fixes without new log evidence.

### When to stop fixing

**Stop and report** (do not merge or claim green) when:

- Failure requires secrets or credentials you cannot access
- Root cause is external (GitHub outage, registry down, quota exceeded)
- Fix needs a product/architecture decision (delete feature vs rewrite)
- Failures are on the default branch unrelated to your branch — report upstream breakage
- After **two focused fix attempts**, the same step fails with a new unrelated error — escalate

## 7. Report

Deliver a structured summary:

```markdown
## CI debug summary

**Repository:** <owner/repo>
**Branch / PR:** <branch> (#<number> if applicable)
**Run:** <url or run id>

### Failure
- **Workflow / job / step:**
- **Category:**
- **Root cause:**

### Evidence
<quoted log excerpt or local repro command + output>

### Fix (if applied)
- **Changes:**
- **Verification:** local command + new CI run id/conclusion

### Remaining blockers
<anything needing user action>
```

## Coordination With Other Skills

| Skill | Role |
|-------|------|
| [github-publish](../github-publish/SKILL.md) | Branch, PR, push, watch checks, merge approval |
| [github-workflows](../github-workflows/SKILL.md) | Correct workflow layout when CI structure is wrong |
| [ci-optimize](../ci-optimize/SKILL.md) | Speed improvements after CI is green |
| [dependabot-merge](../dependabot-merge/SKILL.md) | CI failures on Dependabot PRs |
| [test](../test/SKILL.md) / [lint](../lint/SKILL.md) | Gates after code fixes |
| [docker](../docker/SKILL.md) | Reproduce container-based CI locally |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Guessing without reading logs | `gh run view --log-failed` first |
| `npm install` when CI uses `npm ci` | Mirror CI commands exactly |
| Disabling tests or linters to go green | Fix root cause |
| Broad unrelated refactors while fixing CI | Minimal scoped diff |
| Pushing without local repro | Reproduce when feasible |
| Ignoring matrix shard identity | Read the failing shard's log |
| `--no-verify` or force-push to default | Fix on feature branch |
| Treating infra flakes as code bugs | Re-run once; note persistent flakes |

## Additional Resources

- Command reference and failure examples: [examples.md](examples.md)
