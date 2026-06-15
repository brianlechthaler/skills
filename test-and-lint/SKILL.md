---
name: test-and-lint
description: >-
  Enforce TDD, 100% test coverage on generated code, and linting before commits.
  Use when writing, modifying, or generating code; before staging or committing;
  when the user asks to implement features, fix bugs, refactor, or add tests;
  or when discussing test coverage, linting, or code quality gates.
---

# Test and Lint

## Core Requirements

When applicable to the work at hand:

- All generated code should have **100% test coverage**
- Always use **test driven development (TDD)**
- Avoid committing untested code
- Always **lint** code
- Avoid committing code that has not been linted

These are hard gates. Do not mark work complete, stage changes, or commit until both gates pass.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| New or changed source code (`.ts`, `.py`, `.go`, `.rs`, etc.) | Pure documentation (`.md`) with no code |
| Bug fixes and refactors in testable modules | Generated lockfiles or vendored third-party code |
| New features, APIs, CLI commands, libraries | Repo has no test/lint tooling and user explicitly opts out |
| User asks to commit or open a PR | Config-only edits with no project linter configured |

When unsure, default to **test + lint**. If tooling is missing, add minimal project-standard setup before writing production code.

## TDD Workflow

Follow **Red → Green → Refactor** for every behavior change:

1. **Red** — Write a failing test that describes the desired behavior (one focused case at a time).
2. **Green** — Write the minimum production code to make the test pass.
3. **Refactor** — Clean up while keeping tests green.
4. **Repeat** until the feature or fix is complete.

Rules:

- Never write production code without a failing test first (except trivial scaffolding the project already uses, e.g. empty module exports).
- One logical behavior per test; name tests after behavior, not implementation.
- Do not skip tests to "add them later."

## Coverage Gate (100%)

After tests pass, verify **100% coverage on all code you generated or changed**:

1. Run the project coverage command (see [examples.md](examples.md) for stack-specific commands).
2. Scope coverage to changed files/modules when the tool supports it; otherwise ensure project-wide coverage does not drop and changed files are fully covered.
3. If coverage is below 100% on generated/changed code:
   - Add tests for uncovered lines, branches, and edge cases
   - Remove dead code rather than excluding it from coverage
4. Do not use `# pragma: no cover`, `istanbul ignore`, or `@ts-ignore` to bypass coverage unless the user explicitly requests it and documents why.

Report coverage briefly when finishing (e.g. "100% on `src/foo.ts`").

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
1. Write failing test(s)          ← TDD Red
2. Implement minimal code         ← TDD Green
3. Refactor if needed             ← TDD Refactor
4. Run unit tests                 → must pass
5. Run coverage on changed code   → must be 100%
6. Run linter(s)                  → must pass
7. Only then: stage / commit / PR
```

If the [docker](../docker/SKILL.md) skill applies, run tests and linters **inside the container** — never skip gates because the host lacks tooling.

## Pre-Commit Checklist

Copy and complete before any commit that includes code:

```
Quality gates:
- [ ] Tests written first (TDD)
- [ ] All tests pass
- [ ] 100% coverage on generated/changed code
- [ ] Linter(s) pass on changed code
- [ ] Formatter check passes (if configured)
```

If the user asks to commit and any box is unchecked, run the missing step first. Do not commit untested or unlinted code.

## Detecting Project Tooling

Inspect the repo before the first test or lint run:

| Signal | Tests | Coverage | Lint |
|--------|-------|----------|------|
| `package.json` scripts | `npm test`, `pnpm test` | `vitest --coverage`, `jest --coverage` | `npm run lint`, `eslint`, `prettier --check` |
| `pyproject.toml` / `pytest.ini` | `pytest` | `pytest --cov --cov-fail-under=100` | `ruff check`, `muff`, `mypy` |
| `go.mod` | `go test ./...` | `go test -coverprofile` + inspect | `golangci-lint run`, `go vet` |
| `Cargo.toml` | `cargo test` | `cargo llvm-cov` / `cargo tarpaulin` | `cargo clippy`, `cargo fmt --check` |
| `Makefile` | `make test` | `make coverage` if present | `make lint` |
| Existing CI (`.github/workflows/`) | Mirror CI test command | Mirror CI coverage flags | Mirror CI lint command |

Prefer Makefile/CI commands when they exist — they are the source of truth.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Write code first, tests after | Red → Green → Refactor |
| Commit with failing or skipped tests | Fix or add tests; never `--no-verify` unless user explicitly requests |
| `"Good enough"` coverage (e.g. 80%) | 100% on generated/changed code |
| Lint only changed lines when CI lints whole project | Match CI scope |
| Disable rules or exclude files to pass lint | Fix the code |
| Skip gates on "small" changes | Run gates every time |
| Assume tests pass without running them | Always run tests locally before commit |

## Additional Resources

- Stack-specific coverage and lint commands: [examples.md](examples.md)
