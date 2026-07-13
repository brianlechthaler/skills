# CI Debug — Examples

## Example 1: Failed unit tests on a PR

**Symptoms:** PR checks show `Test` workflow failed.

```bash
BRANCH=$(git branch --show-current)
gh run list --branch "$BRANCH" --limit 5 \
  --json databaseId,conclusion,workflowName,headSha

RUN_ID=1234567890
gh run view "$RUN_ID" --json jobs \
  --jq '.jobs[] | select(.conclusion=="failure") | {name, conclusion}'

gh run view "$RUN_ID" --log-failed
```

**Log excerpt:** `AssertionError: expected 404 to equal 200` in `src/api/routes.test.ts`.

**Reproduce:**

```bash
npm ci
npm test -- src/api/routes.test.ts
```

**Root cause:** Route handler returns 500 when query param is missing; test expects 404.

**Fix:** Adjust handler or test to match intended behavior; push; watch CI.

```bash
git push origin HEAD
gh pr checks --watch
```

## Example 2: Lint failure in CI but not locally

**Symptoms:** `Lint` job failed; local `npm run lint` passes.

```bash
gh run view <run-id> --log-failed | rg -n "error|eslint|ruff"
cat .github/workflows/lint.yml
```

**Discovery:** CI uses Node 20; local host uses Node 18 with different ESLint defaults.

**Reproduce with CI version:**

```bash
nvm use 20   # or: docker run --rm -v "$PWD:/app" -w /app node:20 npm ci && npm run lint
```

**Fix:** Align local tooling or fix violations surfaced under Node 20; optionally document required version in README.

## Example 3: Lockfile mismatch (`npm ci` failure)

**Log excerpt:**

```
npm ERR! `npm ci` can only install packages when your package.json and package-lock.json are in sync
```

**Root cause:** `package.json` changed without updating `package-lock.json`.

**Fix:**

```bash
npm install --package-lock-only   # or npm ci after regenerating on CI's npm major version
npm ci
npm test
git add package-lock.json
git commit -m "fix(ci): sync package-lock.json with package.json"
git push origin HEAD
```

## Example 4: GHCR push 403

**Log excerpt:** `denied: permission_denied: write_package`

**Check workflow:**

```yaml
permissions:
  contents: read
  packages: write   # required on the job that pushes
```

**Also verify:** GitHub **Packages → Package settings → Manage Actions access** links the package to the repo.

## Example 5: Docker build failure in container workflow

```bash
gh run view <run-id> --log-failed
# COPY failed: file not found Dockerfile:12
```

**Reproduce:**

```bash
docker build -t app:ci .
```

**Root cause:** `.dockerignore` excludes a file the Dockerfile copies.

**Fix:** Adjust `.dockerignore` or Dockerfile `COPY` paths; push and re-run `container.yml`.

## Example 6: Workflow syntax / expression error

**Log excerpt:** `Unexpected symbol: '$'`.

```bash
actionlint .github/workflows/test.yml
```

**Root cause:** Invalid `${{ }}` expression or unquoted YAML.

**Fix:** Correct the workflow file; push — no application code change needed.

## Example 7: Matrix shard failure (one of four)

```bash
gh run view <run-id> --json jobs --jq '.jobs[] | {name, conclusion}'
# test (3) failed; test (1), (2), (4) succeeded
```

Fetch logs for the failing shard only:

```bash
gh run view <run-id> --log-failed | rg -A30 "test \(3\)"
```

**Root cause:** Order-dependent test in `tests/integration/db_test.py` — fails when shard 3 runs in parallel.

**Fix:** Isolate test DB per worker or mark serial; not disable the whole matrix.

## Example 8: Stale branch / merge conflict with default

**Symptoms:** CI fails on merge commit or `mergeable: CONFLICTING`.

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin
git merge "origin/$DEFAULT"
# resolve conflicts, run tests
git push origin HEAD
gh pr checks --watch
```

## Example 9: Re-run failed jobs after infra flake

When logs show GitHub service errors or runner allocation failures and code is unchanged:

```bash
gh run rerun <run-id> --failed
gh run watch <run-id>
```

Document as infra flake if green on retry; only change code if failure repeats on the same step.

## Example 10: Debug default-branch CI (no PR)

```bash
gh run list --branch main --limit 5 \
  --json databaseId,conclusion,workflowName,createdAt

gh run view <run-id> --log-failed
```

Report upstream breakage to the user; fix on a feature branch off `main` unless explicitly asked to commit directly to default.

## Quick reference

```bash
# Latest failed runs on current branch
gh run list --branch "$(git branch --show-current)" --limit 10

# Failed logs
gh run view <run-id> --log-failed

# Watch after push
gh run watch <run-id>
gh pr checks --watch

# PR check rollup
gh pr view <number> --json statusCheckRollup
```
