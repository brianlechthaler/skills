---
name: test
description: >-
  Enforce TDD and 100% test coverage on generated code before commits.
  Use when writing, modifying, or generating code; before staging or committing;
  when the user asks to implement features, fix bugs, refactor, or add tests;
  or when discussing test coverage, TDD, or unit tests.
---

# Test

## Core Requirements

When applicable to the work at hand:

- All generated code should have **100% test coverage**
- Always use **test driven development (TDD)**
- Avoid committing untested code

These are hard gates. Do not mark work complete, stage changes, or commit until tests pass and coverage is 100% on generated/changed code.

For linting and formatting gates, follow the [lint](../lint/SKILL.md) skill before commit.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| New or changed source code (`.ts`, `.py`, `.go`, `.rs`, etc.) | Pure documentation (`.md`) with no code |
| Bug fixes and refactors in testable modules | Generated lockfiles or vendored third-party code |
| New features, APIs, CLI commands, libraries | Repo has no test tooling and user explicitly opts out |
| User asks to commit or open a PR | Config-only edits with no project test runner configured |

When unsure, default to **TDD + coverage**. If tooling is missing, add minimal project-standard setup before writing production code.

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

## Execution Order

For each code change cycle:

```
1. Write failing test(s)          ← TDD Red
2. Implement minimal code         ← TDD Green
3. Refactor if needed             ← TDD Refactor
4. Run unit tests                 → must pass
5. Run coverage on changed code   → must be 100%
6. Run linter(s)                  → see lint skill
7. Only then: stage / commit / PR
```

If the [docker](../docker/SKILL.md) skill applies, run tests **inside the container** — never skip gates because the host lacks tooling.

## Pre-Commit Checklist

Copy and complete before any commit that includes code:

```
Test gates:
- [ ] Tests written first (TDD)
- [ ] All tests pass
- [ ] 100% coverage on generated/changed code
```

If the user asks to commit and any box is unchecked, run the missing step first. Do not commit untested code.

## Detecting Project Tooling

Inspect the repo before the first test run:

| Signal | Tests | Coverage |
|--------|-------|----------|
| `package.json` scripts | `npm test`, `pnpm test` | `vitest --coverage`, `jest --coverage` |
| `pyproject.toml` / `pytest.ini` | `pytest` | `pytest --cov --cov-fail-under=100` |
| `go.mod` | `go test ./...` | `go test -coverprofile` + inspect |
| `Cargo.toml` | `cargo test` | `cargo llvm-cov` / `cargo tarpaulin` |
| `Makefile` | `make test` | `make coverage` if present |
| Existing CI (`.github/workflows/`) | Mirror CI test command | Mirror CI coverage flags |

Prefer Makefile/CI commands when they exist — they are the source of truth.

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Write code first, tests after | Red → Green → Refactor |
| Commit with failing or skipped tests | Fix or add tests; never `--no-verify` unless user explicitly requests |
| `"Good enough"` coverage (e.g. 80%) | 100% on generated/changed code |
| Skip gates on "small" changes | Run gates every time |
| Assume tests pass without running them | Always run tests locally before commit |

## Additional Resources

- Stack-specific test and coverage commands: [examples.md](examples.md)
