# Test and Lint — Stack Examples

Use the commands below when the project has no Makefile or CI to mirror. Adapt paths to the files you changed.

## Node / TypeScript (Vitest)

```bash
# TDD: run one test file in watch mode during development
npx vitest run src/foo.test.ts

# Gate: all tests + coverage on changed module
npx vitest run --coverage
# Ensure coverage report shows 100% lines/branches on changed files

# Lint
npm run lint
npx prettier --check .
```

`vitest.config.ts` — scope coverage when needed:

```ts
coverage: {
  include: ["src/foo/**"],
  thresholds: { lines: 100, branches: 100, functions: 100, statements: 100 },
}
```

## Node / TypeScript (Jest)

```bash
npx jest --coverage --collectCoverageFrom='src/foo/**/*.{ts,tsx}'
npx eslint . --max-warnings=0
npx prettier --check .
```

## Python (pytest + ruff)

```bash
# TDD
pytest tests/test_foo.py -x

# Gate
pytest --cov=package.foo --cov-report=term-missing --cov-fail-under=100
ruff check .
ruff format --check .
```

## Go

```bash
go test ./pkg/foo/... -coverprofile=coverage.out
go tool cover -func=coverage.out   # verify 100% on changed packages
golangci-lint run ./...
```

## Rust

```bash
cargo test
cargo llvm-cov --fail-under-lines 100
cargo clippy -- -D warnings
cargo fmt --check
```

## Makefile-driven projects

When `make test`, `make coverage`, or `make lint` exist, use them:

```bash
make test
make coverage    # if target exists
make lint
```

## Docker-wrapped commands

When the [docker](../docker/SKILL.md) skill applies:

```bash
docker compose run --rm app npm test
docker compose run --rm app npm run lint
# or
docker run --rm -v "$(pwd):/workspace" -w /workspace image:tag pytest --cov --cov-fail-under=100
```

## Minimal setup (greenfield)

When adding tooling to a repo with none:

1. Add the stack's standard test runner and one linter (do not over-engineer).
2. Add `test` and `lint` scripts/targets.
3. Configure coverage thresholds at 100% for new modules.
4. Proceed with TDD from that point forward.
