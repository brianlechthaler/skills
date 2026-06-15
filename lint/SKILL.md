---
name: lint
description: >-
  Enforce linting and formatting before commits. Use when writing, modifying,
  or generating code; before staging or committing; when the user asks to
  implement features, fix bugs, or refactor; or when discussing linting,
  formatting, or code style gates.
---

# Lint

## Core Requirements

When applicable to the work at hand:

- Always **lint** code
- Avoid committing code that has not been linted

These are hard gates. Do not mark work complete, stage changes, or commit until linters and formatters pass.

For TDD and coverage gates, follow the [test](../test/SKILL.md) skill before commit.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| New or changed source code (`.ts`, `.py`, `.go`, `.rs`, etc.) | Pure documentation (`.md`) with no code |
| Bug fixes and refactors in lintable modules | Generated lockfiles or vendored third-party code |
| New features, APIs, CLI commands, libraries | Repo has no linter configured and user explicitly opts out |
| User asks to commit or open a PR | Config-only edits with no project linter configured |

When unsure, default to **lint + format check**. If tooling is missing, add minimal project-standard setup before committing code.

## Lint Gate

Before staging or committing:

1. Detect project linters from config files (`eslint`, `ruff`, `golangci-lint`, `clippy`, `prettier`, etc.) and scripts (`npm run lint`, `make lint`).
2. Run linters in **check mode** (not auto-fix-only) on changed files at minimum; run project-wide lint when that is the repo convention.
3. Fix all violations. Re-run until clean.
4. If the project has a formatter, run format check (`prettier --check`, `ruff format --check`, `cargo fmt --check`) and fix before commit.

Prefer auto-fix (`eslint --fix`, `ruff check --fix`, `gofmt`) then re-run check mode to confirm.

## Execution Order

For each code change cycle:

```
1. Write and run tests              → see test skill
2. Run linter(s)                    → must pass
3. Run formatter check (if configured) → must pass
4. Only then: stage / commit / PR
```

If the [docker](../docker/SKILL.md) skill applies, run linters **inside the container** — never skip gates because the host lacks tooling.

## Pre-Commit Checklist

Copy and complete before any commit that includes code:

```
Lint gates:
- [ ] Linter(s) pass on changed code
- [ ] Formatter check passes (if configured)
```

If the user asks to commit and any box is unchecked, run the missing step first. Do not commit unlinted code.

## Detecting Project Tooling

Inspect the repo before the first lint run:

| Signal | Lint |
|--------|------|
| `package.json` scripts | `npm run lint`, `eslint`, `prettier --check` |
| `pyproject.toml` | `ruff check`, `muff`, `mypy` |
| `go.mod` | `golangci-lint run`, `go vet` |
| `Cargo.toml` | `cargo clippy`, `cargo fmt --check` |
| `Makefile` | `make lint` |
| Existing CI (`.github/workflows/`) | Mirror CI lint command |

Prefer Makefile/CI commands when they exist — they are the source of truth.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Lint only changed lines when CI lints whole project | Match CI scope |
| Disable rules or exclude files to pass lint | Fix the code |
| Skip gates on "small" changes | Run gates every time |
| Auto-fix without re-running check mode | Fix, then verify with check mode |
| Commit with `--no-verify` to skip hooks | Fix lint issues; never skip unless user explicitly requests |

## Additional Resources

- Stack-specific lint and format commands: [examples.md](examples.md)
