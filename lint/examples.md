# Lint — Stack Examples

Use the commands below when the project has no Makefile or CI to mirror. Adapt paths to the files you changed.

## Node / TypeScript

```bash
npm run lint
npx eslint . --max-warnings=0
npx prettier --check .
```

## Python (ruff)

```bash
ruff check .
ruff format --check .
```

## Go

```bash
golangci-lint run ./...
```

## Rust

```bash
cargo clippy -- -D warnings
cargo fmt --check
```

## Makefile-driven projects

When `make lint` exists, use it:

```bash
make lint
```

## Docker-wrapped commands

When the [docker](../docker/SKILL.md) skill applies:

```bash
docker compose run --rm app npm run lint
```

## Minimal setup (greenfield)

When adding tooling to a repo with none:

1. Add one linter appropriate to the stack (do not over-engineer).
2. Add a `lint` script/target.
3. Add a formatter check if the stack convention expects it.
4. Run lint gates on every code change from that point forward.
