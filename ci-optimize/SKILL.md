---
name: ci-optimize
description: >-
  Aggressively optimize GitHub Actions and CI pipelines for fastest completion
  time. Baselines wall-clock duration, applies parallelization, caching, path
  filters, job splitting, and other speed techniques, then re-measures after
  every change until no meaningful gains remain. Use when the user asks to
  speed up CI, reduce pipeline time, optimize workflows, or make GitHub Actions
  finish faster.
---

# CI Optimize

## Core Rule

**Optimize CI for speed of completion until further changes no longer yield meaningful gains.** Do not stop after one pass. Baseline duration, apply the highest-impact change, push, measure the new wall-clock time, and repeat.

Speed is the primary objective. Preserve required test coverage and security checks — optimize *how* work runs, not *whether* critical gates exist.

## Prerequisites

```bash
gh auth status
git fetch origin
```

Inspect existing CI:

```bash
ls -la .github/workflows/
gh workflow list
gh run list --limit 10 --json databaseId,displayTitle,conclusion,createdAt,updatedAt,workflowName,headBranch
```

Identify the **critical path** — the slowest workflow/job/step chain that determines when a PR is green.

## Optimization Loop

Copy and track until done:

```
CI optimize progress:
- [ ] Baseline measured (workflow, branch, duration, slowest job/step)
- [ ] Bottleneck ranked (top 3 by wall-clock impact)
- [ ] Change applied (one focused optimization per commit when practical)
- [ ] Pushed and CI re-run observed
- [ ] New duration recorded and compared to baseline
- [ ] Next bottleneck identified or stop criteria met
```

### 1. Measure baseline

For the workflow under optimization (usually PR runs):

```bash
# Latest run on a branch
gh run list --workflow=<name.yml> --branch=<branch> --limit 5 \
  --json databaseId,conclusion,createdAt,updatedAt,displayTitle

# Duration and per-job timing
gh run view <run-id> --json jobs,createdAt,updatedAt,conclusion
gh run view <run-id> --log-failed   # when debugging slow/failing steps
```

Record:

| Field | Value |
|-------|-------|
| Workflow | |
| Branch / PR | |
| Run ID | |
| Wall-clock (createdAt → updatedAt) | |
| Slowest job | |
| Slowest step (from logs) | |

Prefer **median of last 3 green runs** over a single run when flaky or queue-heavy.

### 2. Rank bottlenecks

Order candidates by **time saved × feasibility**. Typical wins (apply what fits the repo):

| Technique | When it helps |
|-----------|---------------|
| **Parallel jobs** | Independent test/lint/build suites run sequentially |
| **Cancel stale runs** | `concurrency` + `cancel-in-progress: true` on PR workflows |
| **Path filters** | Docs-only or single-package changes rerun everything |
| **Dependency caching** | `cache: npm`/`pip`/`go`/`cargo`, `actions/cache`, apt cache |
| **Docker layer cache** | `cache-from`/`cache-to: type=gha` on build-push-action |
| **Shallow checkout** | `fetch-depth: 1` when full history is not needed |
| **Split slow test job** | Matrix by directory, package, or shard index |
| **Fail fast** | Cheapest lint/typecheck job before expensive integration tests |
| **Reuse built artifacts** | Build container once; downstream jobs pull the image/tarball |
| **Smaller/faster runner** | `ubuntu-latest` suffices; avoid oversized custom runners |
| **Remove duplicate work** | Same `npm ci` + lint in three workflows |
| **Conditional jobs** | Skip container publish on PR; skip E2E when label absent |
| **Pin + upgrade actions** | Old setup actions miss built-in caching improvements |

Do **not** remove required gates (security scans, coverage thresholds, release checks) unless the user explicitly accepts the tradeoff.

### 3. Apply one high-impact change

Prefer the change with the largest expected wall-clock reduction. Keep diffs focused — one optimization theme per commit aids bisection.

After editing workflows, validate YAML locally when possible:

```bash
# When actionlint or yamllint is available
actionlint .github/workflows/*.yml
```

### 4. Push and re-measure

Follow [github-publish](../github-publish/SKILL.md) for branch/PR workflow when publishing changes.

Watch the new run:

```bash
gh run watch <run-id>
gh pr checks --watch          # when optimizing via PR
```

Update the progress table:

| Iteration | Change | Before | After | Δ |
|-----------|--------|--------|-------|---|
| 0 | baseline | | | |
| 1 | | | | |

### 5. Repeat or stop

**Continue** when any of these remain:

- Wall-clock dropped ≥5% on the last change (keep going — compound gains)
- A job or step still dominates runtime (>30% of total)
- Obvious duplicate work, missing cache, or serial bottleneck not yet addressed

**Stop** only when **all** are true:

- Last **two** iterations each improved total time by **<3%** (diminishing returns)
- No remaining bottleneck step accounts for >25% of wall-clock without a disproportionate coverage/security cost to fix
- Required checks still pass locally and in CI

Report final summary: baseline → final duration, percent improvement, changes made, and any remaining cost that needs product/architecture tradeoffs.

## GitHub Actions Patterns

### Cancel stale PR runs

```yaml
concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Path filters (monorepo or docs-heavy repos)

```yaml
on:
  pull_request:
    paths:
      - "src/**"
      - "package.json"
      - ".github/workflows/test.yml"
  push:
    paths:
      - "src/**"
```

Pair with a minimal `workflow_dispatch` or `paths-ignore` on docs for full flexibility.

### Fail fast job ordering

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]
  test:
    needs: lint
    runs-on: ubuntu-latest
    steps: [...]
  container:
    needs: test
    runs-on: ubuntu-latest
    steps: [...]
```

Run **lint and unit tests in parallel** when independent; use `needs` only when outputs are required.

### Test sharding (matrix)

```yaml
jobs:
  test:
    strategy:
      fail-fast: true
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npm test -- --shard=${{ matrix.shard }}/4
```

### Reuse container build

Build once in a `build` job, push to GHA cache or a PR-scoped tag; `test` and `lint` jobs `docker pull` or `load: true` from cache instead of rebuilding.

### Shallow checkout

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 1
```

## Monitoring Commands

```bash
# Compare recent run durations for a workflow
gh run list --workflow=test.yml --limit 10 \
  --json databaseId,conclusion,createdAt,updatedAt,headBranch

# Job-level breakdown
gh run view <id> --json jobs --jq '.jobs[] | {name, startedAt, completedAt, conclusion}'

# Open slow run in browser
gh run view <id> --web
```

When GitHub Actions UI shows queue time vs run time, note both — queue fixes (concurrency, fewer redundant workflows) count as wins.

## Coordination With Other Skills

| Skill | Role |
|-------|------|
| [github-workflows](../github-workflows/SKILL.md) | Correct baseline layout (test, lint, container); extend, don't replace |
| [github-publish](../github-publish/SKILL.md) | Branch, PR, CI watch, merge after user approval |
| [docker](../docker/SKILL.md) | Container-first test runs; mirror cache strategy in CI |
| [lint](../lint/SKILL.md) / [test](../test/SKILL.md) | Gates must still pass after optimizations |

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Stopping after one cache tweak | Measure → optimize → measure until stop criteria |
| Disabling tests or linters for speed | Parallelize, shard, cache, or path-filter |
| One mega-workflow with everything serial | Split parallel jobs; share artifacts |
| `fetch-depth: 0` everywhere | Shallow checkout unless history is required |
| Rebuilding Docker image per job | Single build + GHA cache or artifact |
| Optimizing without baseline numbers | Record run IDs and durations every iteration |
| Ignoring queue/cancel waste | Add concurrency; drop redundant triggers |
| `--force` or skipping hooks to merge faster | Fix the pipeline; follow publish workflow |

## Additional Resources

- Copy-paste optimization recipes: [examples.md](examples.md)
