---
name: compiled-performance
description: >-
  Analyze compiled application performance thoroughly with profilers and
  benchmarks, identify bottlenecks in CPU, memory, I/O, and concurrency,
  suggest prioritized optimizations, and optionally implement fixes with
  before/after measurements. Use when the user asks to profile, benchmark,
  optimize, or speed up native binaries, C/C++/Rust/Go/Fortran apps, CLI tools,
  servers, or compiled code performance.
---

# Compiled Performance

Conduct a **thorough, measured performance audit** of compiled/native applications. Baseline wall-clock and resource metrics first, profile hot paths with the right tools, rank optimizations by impact × effort, and optionally implement them with verified gains.

This skill covers **CPU-bound binaries and native runtimes** — not browser page load or CI pipeline duration. For those, use [web-performance](../web-performance/SKILL.md) and [ci-optimize](../ci-optimize/SKILL.md). For heap correctness (not throughput), use [valgrind-memcheck](../valgrind-memcheck/SKILL.md).

## When to Use

| Applies | Does not apply |
|---------|----------------|
| C, C++, Rust, Go, Fortran, Zig, Nim, D, or other AOT/JIT-compiled targets | Pure interpreted Python/JS/Ruby unless profiling native extensions |
| Slow CLI tools, daemons, game engines, codecs, parsers, numerical code | Web Core Web Vitals, bundle size, Lighthouse (use web-performance) |
| High CPU, memory, allocation, cache-miss, or I/O latency | GitHub Actions wall-clock (use ci-optimize) |
| User asks to profile, benchmark, flamegraph, optimize, or "make it faster" | Memory leaks / use-after-free (use valgrind-memcheck) |

When unsure on a native codebase, default to **baseline + CPU profile + allocation profile** before recommending changes.

## Implement Mode (decide first)

| User intent | Behavior after audit |
|-------------|----------------------|
| Default — "analyze performance", "profile this binary", "find bottlenecks" | Deliver findings and recommendations, then **ask** whether to implement optimizations |
| Explicit implement — "profile and fix", "optimize and implement", "make it faster" (with implementation implied) | **Skip the prompt** — implement highest-impact fixes immediately after the report |

When implementing:

1. Fix in priority order: Critical → High → Medium → Low
2. Re-measure after each batch; keep before/after numbers in the report
3. Follow [test](../test/SKILL.md) and [lint](../lint/SKILL.md) after code changes
4. Prefer minimal, targeted diffs — see [simple-code](../simple-code/SKILL.md)
5. Follow [github-publish](../github-publish/SKILL.md) when publishing fixes via PR
6. Do **not** commit unless the user asks

When prompting (default), use AskQuestion when available:

- **Prompt**: "Implement the recommended performance optimizations?"
- **Options**: "Yes — implement all" (recommended when Critical/High exist), "Yes — Critical and High only", "No — report only"

If AskQuestion is unavailable, ask conversationally with the same options.

## Prerequisites

1. **Runnable binary or benchmark target** — entry point, args, env vars, and representative workload
2. **Build with profiling symbols** — debug info + realistic optimization (see Build Profiles below)
3. **Profiler available** — install or use container; see [examples.md](examples.md)
4. **Reproducible workload** — fixed input, iteration count, or benchmark harness so numbers are comparable

On Linux, verify `perf` access when needed: `perf stat echo ok` (may require `sudo` or `kernel.perf_event_paranoid ≤ 2`).

## Build Profiles

Profile with **production-like optimization**, not pure debug builds:

| Language / build | Recommended flags |
|------------------|-------------------|
| C/C++ (GCC/Clang) | `-g -O2` or `-g -O3 -march=native` for release-like local runs |
| CMake | `-DCMAKE_BUILD_TYPE=RelWithDebInfo` |
| Rust | `cargo build --release` (debug symbols in release via `debug = true` in `[profile.release]` when line numbers matter) |
| Go | Default release build; use `-gcflags=all=-l` only when investigating inlining |

Use `-O0` only when line-level accuracy matters more than realistic timing. Always note the build flags in the report.

## Audit Workflow

Copy and track progress:

```
Compiled performance audit:
- [ ] Phase 0: Recon — language, build system, entry points, workload
- [ ] Phase 1: Baseline — wall time, CPU, memory, throughput
- [ ] Phase 2: CPU profiling — hot functions, flame graph, samples
- [ ] Phase 3: Memory and allocations — heap churn, peak RSS, cache behavior
- [ ] Phase 4: I/O and blocking — syscalls, disk, network, locks
- [ ] Phase 5: Algorithm and data layout — complexity, copies, cache locality
- [ ] Phase 6: Concurrency — threads, contention, false sharing, oversubscription
- [ ] Phase 7: Report — prioritized findings with evidence and estimates
- [ ] Phase 8: Implement — prompt or auto-fix
```

Run phases **in order**. Do not recommend fixes without measurements for the affected area.

### Phase 0 — Recon

Map the performance surface before profiling:

- Language, compiler, build system (Make, CMake, Cargo, go.mod, Meson, Bazel)
- Binary(ies) to profile and how to build them
- Representative workload: CLI args, input files, request rate, benchmark name
- Existing benchmarks (`benchmark/`, Google Benchmark, Criterion, Go `testing.B`, pytest benchmarks for extensions)
- Deployment constraints: single-thread vs parallel, latency vs throughput SLO
- Prior perf work: PGO/LTO flags, custom allocators, SIMD intrinsics

Read manifests and README. Identify the **critical path** the user cares about (p99 latency, jobs/sec, frames/sec, etc.).

### Phase 1 — Baseline

Measure **before** proposing fixes. Run the workload at least **3 times**; report median (or mean ± stdev if variance is high).

**Record in the report:**

| Metric | Command / source | Value |
|--------|------------------|-------|
| Wall time | `time`, `/usr/bin/time -v`, hyperfine | |
| CPU time (user/sys) | `time -v`, `perf stat` | |
| Peak RSS | `time -v`, `/proc`, `ps` | |
| Throughput | ops/sec, req/sec, MB/sec from benchmark | |
| Allocations (if applicable) | heap profiler, `perf stat` | |

Prefer [hyperfine](https://github.com/sharkdp/hyperfine) for CLI timing:

```bash
hyperfine --warmup 3 --min-runs 5 './myapp --input benchmark.dat'
```

Use the project's existing benchmark target when present (`make bench`, `cargo bench`, `go test -bench=.`, `ctest -R bench`).

### Phase 2 — CPU Profiling

Pick the **default tool for the stack**, then deepen if needed:

| Stack | Default tool | Deeper options |
|-------|--------------|----------------|
| Linux native (C/C++/Rust) | `perf record` + flame graph | `perf annotate`, Intel VTune, `cachegrind` |
| macOS native | `sample`, Instruments Time Profiler | `dtrace` |
| Go | `go test -cpuprofile` / `pprof` | `trace`, `fgprof` |
| Rust | `cargo flamegraph` / `perf` | `samply`, `iai` for micro-benches |
| Java / Kotlin | `async-profiler`, JFR | VisualVM |
| .NET | `dotnet-trace`, `dotnet-counters` | PerfView |

**Linux perf (generic native binary):**

```bash
perf record -g --call-graph dwarf -F 997 -- ./myapp args
perf report --stdio | head -80
# Flame graph (when infer/flamegraph installed):
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg
```

Read the profile **top-down**: identify functions accounting for ≥5% of samples (or the user's stated SLO gap). Note caller chains, not just leaf functions.

### Phase 3 — Memory and Allocations

When RSS grows, GC pauses matter, or the profile shows allocator overhead:

| Tool | Use for |
|------|---------|
| `heaptrack` | Allocation counts and call stacks (C/C++) |
| `massif` / `ms_print` (Valgrind) | Peak heap over time |
| Go `pprof -alloc_space` | Go allocation hot spots |
| Rust `dhat`, `heaptrack` | Rust allocation patterns |
| `perf stat -d` | Cache misses, page faults (hardware counters) |

Distinguish **allocation rate** vs **peak footprint** vs **fragmentation**. Recommend pool allocators, stack buffers, or `reserve()` only when data supports it.

### Phase 4 — I/O and Blocking

When CPU profile is flat but wall time is high:

- Trace syscalls: `strace -c`, `perf trace`, `go tool trace`
- Check blocking I/O: sync disk writes, fsync per op, unbuffered reads
- Network: connect timeouts, N+1 RPC patterns, missing keep-alive
- Locks: `perf lock`, TSan-free mutex contention in `perf top`, Go mutex profile

### Phase 5 — Algorithm and Data Layout

Code review guided by profile evidence:

- Time complexity vs input size (measure at 1×, 10×, 100× scale)
- Avoidable copies, `std::move` opportunities, pass-by-reference
- Cache locality: AoS vs SoA, struct padding, false sharing
- Branch prediction: hot/cold split, lookup tables vs branches
- SIMD/auto-vectorization: `-Rpass-missed=.*` (Clang), `-fopt-info-vec` (GCC)
- String concatenation in loops, repeated parsing, redundant hash lookups

### Phase 6 — Concurrency

When using threads, goroutines, or async runtimes:

- CPU oversubscription vs underutilization
- Lock contention and critical section size
- Work-stealing / queue depth / batching opportunities
- False sharing on atomics or padded counters
- Go: `GOMAXPROCS`, scheduler trace; Rust: `rayon` thread pool sizing

### Phase 7 — Report

Deliver a structured report. For large audits with many findings, use the [canvas](../canvas/SKILL.md) skill for interactive layout.

```markdown
# Compiled Performance Report — <binary or component>

## Executive summary
<1–3 sentences: primary bottleneck, estimated headroom, top recommendation>

## Environment
- Binary: `<path>` (built with `<flags>`)
- Workload: `<command + input>`
- Platform: `<OS, CPU model, cores>`
- Tools: `<perf, hyperfine, …>`

## Baseline
| Metric | Before |
|--------|--------|
| Wall time | |
| CPU (user/sys) | |
| Peak RSS | |
| Throughput | |

## Hot path (CPU)
<top 5–10 functions with % samples; attach or describe flame graph>

## Findings

### PERF-001: <short title>
- **Severity**: Critical / High / Medium / Low
- **Category**: CPU / Memory / I/O / Algorithm / Concurrency / Build
- **Location**: `<file>:<line>` or `<function>`
- **Evidence**: <profile snippet, benchmark delta, counter data>
- **Impact**: <expected gain — e.g. "~40% wall time on benchmark X">
- **Recommendation**: <specific change>
- **Effort**: Low / Medium / High

(repeat per finding)

## Optimization roadmap
| Priority | Finding | Est. impact | Effort |
|----------|---------|-------------|--------|
| 1 | | | |

## Clean areas
<components already efficient; avoid unnecessary churn>

## Next steps
<re-profile command; PGO/LTO trial; benchmark to add>
```

Sort findings by severity and estimated impact. Every recommendation must cite **measurement or profile data** — no speculative micro-optimizations without evidence.

Full per-phase checklists: [checklist.md](checklist.md)

### Phase 8 — Implement

Apply fixes from the roadmap when the user opts in or requested implement mode.

1. One logical optimization per commit when practical
2. Re-run the **same baseline commands** after each batch
3. Update the report's before/after table
4. Stop when gains plateau or remaining items are Low severity with High effort
5. If a change regresses correctness, revert and note in the report

## Quick Reference — Common Fixes

| Symptom | Likely cause | Typical fix |
|---------|--------------|-------------|
| Hot `malloc`/`free` | Per-item allocation in loop | Preallocate, object pool, `reserve()` |
| Hot `memcpy` | Unnecessary copies | References, move semantics, in-place |
| High cache-miss rate | Poor locality | SoA layout, reorder loops, shrink structs |
| Flat CPU, slow wall | I/O or locks | Batch I/O, async, shrink critical sections |
| Scales poorly with N | O(n²) or worse | Better algorithm, index, hash map |
| Slow debug-only | `-O0` build | Profile RelWithDebInfo / release |

Stack-specific commands and build recipes: [examples.md](examples.md)

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Optimizing without baseline | Measure first; keep numbers in the report |
| `-O0` profiling for release SLOs | RelWithDebInfo / release + debug symbols |
| Premature SIMD / intrinsics | Fix algorithm and allocations first unless profile proves CPU-bound math |
| Micro-optimizing cold paths | Focus on ≥5% sample share or measured wall-time share |
| Single-run timings | Multiple runs; report median |
| Removing safety checks for speed | Optimize hot path; keep checks on cold/error paths |
| Implementing every Low finding | Ask user or stop at diminishing returns |

## Additional Resources

- Stack-specific profiling recipes: [examples.md](examples.md)
- Detailed audit checklists: [checklist.md](checklist.md)
- Containerized profiling (no host install): [docker](../docker/SKILL.md)
- Memory correctness after aggressive changes: [valgrind-memcheck](../valgrind-memcheck/SKILL.md)
