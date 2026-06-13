# GitHub Workflow Examples

Language-specific starting points. Adapt commands, versions, and paths to the repo.

## Python — test.yml

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
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest
```

## Python — lint.yml

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install ruff
      - run: ruff check .
      - run: ruff format --check .
```

## Go — test.yml

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
          cache: true
      - run: go test -race -cover ./...
```

## Go — lint.yml

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - uses: golangci/golangci-lint-action@v6
        with:
          version: latest
```

## Rust — test.yml + lint.yml (combined jobs, separate workflows recommended)

**test.yml:**

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --all-features
```

**lint.yml:**

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - uses: Swatinem/rust-cache@v2
      - run: cargo fmt --all -- --check
      - run: cargo clippy --all-features -- -D warnings
```

## Makefile-driven project

When the repo documents `make test` and `make lint`:

```yaml
# test.yml
- run: make test

# lint.yml
- run: make lint
```

Ensure the workflow installs any tools the Makefile expects, or run inside the project Docker image.

## Monorepo path filters

Scope workflows to subdirectories that changed:

```yaml
on:
  push:
    branches: [main]
    paths:
      - "services/api/**"
      - ".github/workflows/test.yml"
  pull_request:
    paths:
      - "services/api/**"
      - ".github/workflows/test.yml"
```

## Reusable workflow (org-wide container publish)

Caller `.github/workflows/container.yml`:

```yaml
name: Container

on:
  push:
    branches: [main]
    tags: ["v*"]

jobs:
  publish:
    uses: my-org/.github/.github/workflows/container-reusable.yml@main
    permissions:
      contents: read
      packages: write
    secrets: inherit
```

Use reusable workflows only when the same GHCR pattern is shared across many repos; otherwise keep the template inline for clarity.
