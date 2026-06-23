---
name: valgrind-memcheck
description: >-
  Run Valgrind Memcheck on C/C++ binaries to detect memory leaks, invalid
  reads/writes, use-after-free, double free, and uninitialised values.
  Produce detailed reports of findings and offer to fix issues. Use when
  the user asks to check for memory leaks, run valgrind or memcheck, debug
  heap corruption, or verify native code memory safety.
---

# Valgrind Memcheck

Use Valgrind's **Memcheck** tool to find heap errors and memory leaks in C/C++ programs. Start from the [Valgrind Quick Start Guide](https://valgrind.org/docs/manual/quick-start.html); use the [Memcheck manual](https://valgrind.org/docs/manual/mc-manual.html) for full flag and error-message reference.

## When to Use

| Applies | Does not apply |
|---------|----------------|
| Suspected memory leaks (RSS growth, OOM over time) | Managed languages (Go, Java, Python) unless debugging native extensions |
| Heap corruption, segfaults, use-after-free, double free | Static/stack buffer overruns only (Memcheck may miss these) |
| Uninitialised value reads | Production profiling (Memcheck is slow; use other Valgrind tools) |
| User asks to "run valgrind", "check for leaks", or "memcheck" | Code with no native binary to run under Memcheck |

When unsure on a C/C++ codebase, default to **Memcheck with leak checking** before marking native memory work complete.

## Prerequisites

1. **Valgrind installed** — verify with `valgrind --version`. If missing:
   - Debian/Ubuntu: `sudo apt-get install valgrind`
   - Fedora: `sudo dnf install valgrind`
   - macOS: `brew install valgrind` (limited on Apple Silicon)
   - Or run in a container — see [examples.md](examples.md) and the [docker](../docker/SKILL.md) skill
2. **Debug symbols** — compile with `-g` so stack traces show source line numbers
3. **Optimisation level** — prefer `-O0` for accurate line numbers; `-O1` is usually acceptable; avoid `-O2+` (more false positives)
4. **Runnable binary** — know the program entry point and any required args or env vars

## Workflow

Copy and track progress:

```
Memcheck progress:
- [ ] Confirm valgrind is available (install or container if needed)
- [ ] Build target with -g (and -O0 when practical)
- [ ] Run valgrind --leak-check=full on the binary (+ args)
- [ ] Parse errors and leaks; produce detailed report (template below)
- [ ] Offer to fix findings (unless user asked to fix automatically)
- [ ] Re-run Memcheck after fixes until clean or user stops
```

### 1. Build with debug symbols

```bash
gcc -g -O0 -o myprog src/*.c
# or for C++:
g++ -g -O0 -o myprog src/*.cpp
```

Use the project's existing build (Make, CMake, Meson) but ensure debug flags are enabled for the Memcheck run.

### 2. Run Memcheck

Default command (Memcheck is the default tool):

```bash
valgrind --leak-check=full ./myprog arg1 arg2
```

Recommended flags for thorough reports:

```bash
valgrind \
  --leak-check=full \
  --show-leak-kinds=all \
  --track-origins=yes \
  --verbose \
  ./myprog arg1 arg2
```

| Flag | Purpose |
|------|---------|
| `--leak-check=full` | Detailed leak report with definite/indirect/possible categories |
| `--show-leak-kinds=all` | Include all leak kinds in summary |
| `--track-origins=yes` | Trace origins of uninitialised values (slower, clearer) |
| `--num-callers=N` | Deeper stack traces when default is too shallow |
| `--log-file=memcheck.log` | Save output for the report |

Expect **20–30× slowdown** and higher memory use. Run the smallest reproducer (unit test binary, minimal CLI) when possible.

### 3. Interpret output

Fix errors **in the order reported** — later errors often cascade from earlier ones.

**Invalid access** (overrun, use-after-free, invalid read/write):

```
==19182== Invalid write of size 4
==19182==    at 0x804838F: f (example.c:6)
==19182==    by 0x80483AB: main (example.c:11)
==19182==  Address 0x1BA45050 is 0 bytes after a block of size 40 alloc'd
==19182==    at 0x1B8FF5CD: malloc (vg_replace_malloc.c:130)
==19182==    by 0x8048385: f (example.c:5)
```

Read stack traces **bottom-up** (caller → callee). Note file:line, access type, and allocation site.

**Memory leaks**:

```
==19182== 40 bytes in 1 blocks are definitely lost in loss record 1 of 1
==19182==    at 0x1B8FF5CD: malloc (vg_replace_malloc.c:130)
==19182==    by 0x8048385: f (a.c:5)
==19182==    by 0x80483AB: main (a.c:11)
```

| Leak kind | Meaning | Action |
|-----------|---------|--------|
| **definitely lost** | No pointer to the block remains | Fix — real leak |
| **indirectly lost** | Lost via a definitely-lost parent | Fix with parent |
| **possibly lost** | Interior pointer or unusual ownership | Investigate; often fix |
| **still reachable** | Pointer exists at exit but never freed | Fix if not intentional (e.g. singleton) |
| **suppressed** | Hidden by default suppressions | Review if in your code vs library |

**LEAK SUMMARY** aggregates bytes and block counts per category.

**Uninitialised values**: look for `Conditional jump or move depends on uninitialised value(s)` — rerun with `--track-origins=yes` if the source is unclear.

For unfamiliar messages, see [Explanation of errors (Memcheck manual)](https://valgrind.org/docs/manual/mc-manual.html#mc-manual.errormessages).

## Detailed Report

After Memcheck completes, deliver a structured report. Do not dump raw Valgrind output without analysis.

```markdown
# Valgrind Memcheck Report — <binary or test name>

## Executive summary
<1–3 sentences: clean vs N errors, leak totals, severity>

## Environment
- Binary: `<path>` (built with `<flags>`)
- Command: `valgrind <flags> <cmd>`
- Valgrind version: `<from valgrind --version>`

## Error summary
| Category | Count | Severity |
|----------|-------|----------|
| Invalid read/write | | Critical |
| Use after free | | Critical |
| Double free | | Critical |
| Uninitialised value | | High |
| Definitely lost | | High |
| Possibly lost | | Medium |
| Still reachable | | Low / informational |

## Findings

### Finding 1: <short title>
- **Type**: Invalid write / definitely lost / …
- **Location**: `<file>:<line>` in `<function>`
- **Stack trace** (relevant frames):
  - `main` (main.c:11) → `f` (a.c:5) → `malloc`
- **Explanation**: <what went wrong in plain language>
- **Suggested fix**: <free the allocation / bounds-check index / …>

(repeat per distinct issue)

## Leak summary
<paste or summarise LEAK SUMMARY block>

## Clean areas
<tests or modules that passed Memcheck, if scoped run>

## Next steps
<re-run command after fixes; suppressions only for unfixable third-party noise>
```

If Memcheck reports **no errors** and zero definite leaks, state that explicitly with the command used.

## Fix Mode (decide after reporting)

| User intent | Behavior |
|-------------|----------|
| Default — "check for leaks", "run valgrind" | Deliver report, then **ask** whether to fix findings |
| Explicit — "find and fix leaks", "fix memcheck errors" | Fix immediately after report |

When fixing:

1. Address **invalid accesses and use-after-free before leaks** (same order as Valgrind output)
2. Match project style; prefer `free`/`delete` paired with alloc, RAII in C++, or clear ownership
3. Re-run Memcheck on the same command until errors are resolved or the user accepts remaining items
4. Do **not** commit unless the user asks
5. Follow [test](../test/SKILL.md) and [lint](../lint/SKILL.md) when fixes touch testable code

When prompting (default), ask: **"Fix the Memcheck findings?"** with options for all findings, critical-only, or report-only.

## Quick-Start Example (verified)

From the [Valgrind quick start](https://valgrind.org/docs/manual/quick-start.html) — intentional overrun and leak:

```c
#include <stdlib.h>

void f(void)
{
   int* x = malloc(10 * sizeof(int));
   x[10] = 0;        // problem 1: heap block overrun
}                    // problem 2: memory leak -- x not freed

int main(void)
{
   f();
   return 0;
}
```

```bash
gcc -g -O0 -o a a.c
valgrind --leak-check=full ./a
```

Expected detections:

- `Invalid write of size 4` at the overrun line
- `40 bytes in 1 blocks are definitely lost`
- `ERROR SUMMARY: 2 errors from 2 contexts`

Fixes: use valid index `x[9]` (or allocate 11 elements) and `free(x)` before `f` returns.

## Additional Resources

- [Valgrind Quick Start Guide](https://valgrind.org/docs/manual/quick-start.html)
- [Memcheck User Manual](https://valgrind.org/docs/manual/mc-manual.html)
- [Valgrind FAQ](https://valgrind.org/docs/manual/faq.html)
- Stack-specific build/run patterns: [examples.md](examples.md)
