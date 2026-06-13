---
name: github-workflows
description: >-
  Create and maintain GitHub Actions workflows for CI/CD. Always adds workflows
  for unit tests, linters, and container builds with GHCR publish. Use when
  setting up CI, creating or editing .github/workflows, GitHub Actions, GHCR,
  container publishing, or when the user asks for workflow automation.
---

# GitHub Workflows

## Core Rule

When adding or updating CI for a project, **always** create separate workflows (or jobs with clear separation) for:

1. **Unit tests** — run the project's test suite on every relevant trigger
2. **Linters** — run formatters/checkers; fail on violations
3. **Container builds** — build the image and **publish artifacts to GHCR** (`ghcr.io`)

Do not ship CI without all three when the project has code to test, lint, and containerize. If one category does not apply (no Dockerfile, no linter configured), document why in the workflow file or PR and skip only that piece.

## Before Writing Workflows

Inspect the repo and match existing conventions:

| Signal | Workflow implication |
|--------|----------------------|
| `package.json` + `npm test` / `pnpm test` / `yarn test` | Node test job |
| `pyproject.toml` / `requirements*.txt` + `pytest` | Python test job |
| `go.mod` | `go test ./...` |
| `Cargo.toml` | `cargo test` |
| `Makefile` with `test`, `lint` targets | Prefer `make test`, `make lint` |
| `Dockerfile` / `docker-compose.yml` | Container build job |
| `.eslintrc*`, `ruff`, `golangci-lint`, `clippy`, `prettier` | Linter choice |
| Existing `.github/workflows/` | Extend or align naming/triggers; avoid duplicate jobs |

Prefer running tests and linters **inside the same container image** the project ships when a `Dockerfile` exists. See the [docker](../docker/SKILL.md) skill for container-first local runs; mirror that image in CI.

## Standard Layout

```
.github/workflows/
├── test.yml      # unit tests
├── lint.yml      # linters / format checkers
└── container.yml # build + push to GHCR
```

Use one workflow per concern so failures are isolated and reruns are cheap. Share triggers across files (`push` to `main`, `pull_request`).

## Shared Conventions

### Triggers

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

Add `workflow_dispatch` when manual runs are useful (releases, debugging).

### Permissions (least privilege)

```yaml
permissions:
  contents: read
```

Grant extra permissions only in the job that needs them:

| Job | Extra permissions |
|-----|-------------------|
| GHCR publish | `packages: write` |
| Release / tag push | `contents: write` (only if creating releases) |

### Concurrency (cancel stale PR runs)

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Checkout

```yaml
- uses: actions/checkout@v4
```

## 1. Unit Tests (`test.yml`)

**Goal:** Prove the code works; fail fast on regressions.

**Pattern:**
1. Checkout
2. Set up runtime (or run in container)
3. Install deps with caching
4. Run tests (non-interactive; no watch mode)

**Node example:**

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: test-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
      - run: npm ci
      - run: npm test --if-present
```

**Container-backed tests** (when Dockerfile defines the test environment):

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: app:test
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - run: docker run --rm app:test npm test
```

Adapt the test command to the project (`pytest`, `go test ./...`, `cargo test`, `make test`).

## 2. Linters (`lint.yml`)

**Goal:** Enforce style and static checks; use `--check` / `--diff` modes (never auto-commit from CI unless explicitly requested).

Run only the linters the project already uses. Common mappings:

| Stack | Typical commands |
|-------|------------------|
| Node | `npm run lint`, `npx prettier --check .`, `npx eslint .` |
| Python | `ruff check .`, `ruff format --check .`, `mypy .` |
| Go | `golangci-lint run`, `go vet ./...` |
| Rust | `cargo clippy -- -D warnings`, `cargo fmt --check` |

**Example:**

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: lint-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
      - run: npm ci
      - run: npm run lint --if-present
```

Pin action versions (`@v4`, `@v6`). Add a job per linter only when necessary.

## 3. Container Build + GHCR (`container.yml`)

**Goal:** Build the production image and publish to GitHub Container Registry.

### GHCR image name

```
ghcr.io/<owner>/<image-name>:<tag>
```

Use `github.repository_owner` and a lowercase image name (often the repo name):

```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```

GitHub requires lowercase package names:

```yaml
IMAGE_NAME: ${{ github.repository_owner }}/my-app  # lowercase manually if needed
```

### Required job permissions

```yaml
permissions:
  contents: read
  packages: write
```

### Login, build, push

Use `GITHUB_TOKEN` (no extra secrets for same-repo GHCR publish):

```yaml
name: Container

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
    branches: [main]

concurrency:
  group: container-${{ github.ref }}
  cancel-in-progress: true

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Behavior:**
- **PRs:** build only (verify Dockerfile); `push: false` avoids polluting the registry
- **`main` / tags:** push to GHCR with branch, SHA, and semver tags
- **Cache:** `type=gha` for faster rebuilds

### Multi-platform (optional)

Add `platforms: linux/amd64,linux/arm64` to `docker/build-push-action` when the project targets ARM (e.g. Apple Silicon deploys, Raspberry Pi).

### Package visibility

New GHCR packages may default to private. Link the package to the repo in GitHub **Packages → Package settings → Manage Actions access** so workflow `GITHUB_TOKEN` can push. Tell the user if first push fails with 403.

## Agent Checklist

When creating or updating GitHub Actions for a project:

- [ ] `test.yml` runs the real test suite (not a placeholder)
- [ ] `lint.yml` runs project-configured linters in check mode
- [ ] `container.yml` builds the image and publishes to `ghcr.io` on `main`/tags
- [ ] PR builds verify the image without pushing (or push to a PR-specific tag only if the team wants it)
- [ ] Permissions are minimal; `packages: write` only on the container job
- [ ] Action versions pinned (`@v4`, `@v6`, etc.)
- [ ] Dependency caching enabled where supported
- [ ] Concurrency cancels outdated runs on the same branch
- [ ] Secrets are not hardcoded; use `GITHUB_TOKEN` or repo secrets
- [ ] Workflow names and job names are clear in the Actions UI

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| One mega-workflow with unrelated jobs | Separate `test`, `lint`, `container` workflows |
| Container build without GHCR push on release branches | Always publish to `ghcr.io` on `main`/tags |
| `curl \| bash` in CI without pinning | Use official setup actions or the project Dockerfile |
| Pushing images on every PR | Build on PR; push only on `main`/tags |
| `permissions: write-all` | Scope per job |
| Skipping tests/lint because Docker exists | Run tests in the image or parallel native job |
| Unpinned `@main` actions | Pin major version tags |

## Additional Resources

- Full copy-paste templates per language: [examples.md](examples.md)
