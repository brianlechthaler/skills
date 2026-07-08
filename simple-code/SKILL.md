---
name: simple-code
description: >-
  Write the simplest possible code with the fewest lines — no redundant logic,
  abstractions, or helpers. Use when implementing features, fixing bugs, or
  refactoring; when the user asks for simple, minimal, terse, or concise code;
  or when reducing complexity and line count.
---

# Simple Code

Write the **simplest correct solution** in the **fewest lines**. Every line must earn its place.

## Core Rule

**Solve the problem directly.** Prefer one clear path over layers, wrappers, and defensive extras the task does not need.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| Writing or changing source code | Pure documentation with no code |
| User asks for simple, minimal, or fewer lines | Security, validation, or error handling the task requires |
| Implementing features, fixes, refactors | Removing features or changing APIs without approval |
| Cleaning up redundant logic | Vendored or generated code |

When unsure, default to the smaller, more direct version.

## Principles

1. **Fewest lines** — If two solutions work, pick the shorter one that stays readable.
2. **No redundancy** — No duplicate logic, dead code, unused imports, or pass-through wrappers.
3. **No premature abstraction** — No helpers, classes, or indirection used once or "for later."
4. **Use the language** — Built-ins, stdlib, and idioms before custom machinery.
5. **Scope only** — Implement what was asked; no speculative options or extensibility hooks.
6. **Flat over nested** — Guard clauses and early returns instead of deep nesting.
7. **Data over ceremony** — Maps, literals, and direct calls over boilerplate.

## Writing Checklist

Before finishing code:

```
Simple-code check:
- [ ] No logic duplicated elsewhere in the change
- [ ] No single-use helpers or thin wrappers
- [ ] No unused variables, imports, or branches
- [ ] Nesting is as flat as clarity allows
- [ ] Every added line is required for the task
```

## Limits

Do **not** sacrifice correctness, required validation, or readability for fewer lines.

| Avoid | Do instead |
|-------|------------|
| Cryptic one-liners | Short idiomatic code |
| Removing required error handling | Drop only redundant handling |
| Big-bang rewrites | Smallest diff that simplifies |
| Deleting tests to shrink LOC | Keep tests; simplify implementation |

For test and lint gates before commit, see [test](../test/SKILL.md) and [lint](../lint/SKILL.md).

## Additional Resources

- Before/after patterns: [examples.md](examples.md)
