# CI Optimize — Examples

## Example 1: Baseline and iterate on a Node repo

**Starting point:** `test.yml` + `lint.yml` each run `npm ci` (~90s) and total PR CI ~12 minutes.

**Iteration 1 — concurrency**

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Result: stale runs cancel; effective wait drops when pushing fixups.

**Iteration 2 — parallel lint + test**

Remove cross-workflow duplication; single workflow with parallel jobs sharing setup via a reusable workflow or composite action, or keep two workflows but ensure both use `cache: npm` and run concurrently (not `needs` between them).

**Iteration 3 — path filters**

```yaml
on:
  pull_request:
    paths-ignore:
      - "**.md"
      - "docs/**"
```

Result: docs-only PRs skip CI (~12 min → 0 for those PRs).

**Final report:**

| Metric | Before | After |
|--------|--------|-------|
| Median PR CI (code changes) | 12m 10s | 4m 45s |
| Docs-only PR | 12m 10s | skipped |

## Example 2: Docker-heavy pipeline

**Problem:** `container.yml` rebuilds image; `test.yml` rebuilds the same image.

**Fix:** One `build` job with GHA cache; test job consumes the loaded image:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          load: true
          tags: app:ci
          cache-from: type=gha
          cache-to: type=gha,mode=max

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker run --rm app:ci npm test
```

Measure: compare `build` + `test` job times before/after removing duplicate builds.

## Example 3: Slow pytest suite

**Problem:** `pytest` ~18 minutes serial.

**Fix:** four-way shard matrix:

```yaml
jobs:
  test:
    strategy:
      fail-fast: true
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: pytest --shard-id=${{ matrix.shard }} --num-shards=4
```

Expected wall-clock ≈ longest shard (~5–6 min) plus setup overhead.

## Example 4: Measurement script

```bash
WORKFLOW=test.yml
BRANCH=feat/speed-up-ci

echo "run_id,conclusion,seconds"
gh run list --workflow="$WORKFLOW" --branch="$BRANCH" --limit 5 \
  --json databaseId,conclusion,createdAt,updatedAt \
  --jq '.[] | [.databaseId, .conclusion,
    ((.updatedAt | fromdateiso8601) - (.createdAt | fromdateiso8601))] | @csv'
```

Use output to confirm each optimization iteration shortened median duration.

## Example 5: Stop criteria met

After five iterations:

| # | Change | Duration |
|---|--------|----------|
| 0 | baseline | 11m 42s |
| 1 | concurrency | 11m 05s |
| 2 | npm cache (both workflows) | 8m 20s |
| 3 | parallel lint/test | 5m 10s |
| 4 | pytest shards | 4m 55s |
| 5 | fetch-depth: 1 | 4m 50s |

Iterations 4→5 saved <3%; no step >25% of total except pytest shards (already split). **Stop** and document remaining 4m 50s as acceptable or flag E2E suite for future architectural split.
