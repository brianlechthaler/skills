# Compiled Performance Checklists

Reference for [SKILL.md](SKILL.md). Work through every applicable item — mark N/A only with evidence.

## Phase 0 — Recon

- [ ] Language(s) and compiler(s) identified
- [ ] Build system and release build command documented
- [ ] Entry binary(ies) and typical CLI args / config
- [ ] Representative input or workload defined (file, dataset, request pattern)
- [ ] Performance goal stated (latency p99, throughput, memory cap, realtime deadline)
- [ ] Existing benchmarks or perf tests located
- [ ] Prior optimizations noted (PGO, LTO, custom allocators, SIMD)

## Phase 1 — Baseline

- [ ] Workload run ≥3 times; median (or mean ± stdev) recorded
- [ ] Wall time captured (`hyperfine`, `time -v`, or benchmark harness)
- [ ] CPU user/system time recorded
- [ ] Peak RSS or memory high-water mark recorded
- [ ] Throughput metric recorded when applicable
- [ ] Baseline table filled in report before any recommendations

## Phase 2 — CPU Profiling

- [ ] Correct profiler selected for stack (perf, pprof, flamegraph, Instruments, etc.)
- [ ] Profile captured on release-like build (`-O2`/`-O3` or `--release`)
- [ ] Top hot functions identified (≥5% samples or clear wall-time share)
- [ ] Call chains understood (not only leaf functions)
- [ ] Flame graph or equivalent visualization produced when useful
- [ ] Idle/wait time distinguished from CPU-bound work

## Phase 3 — Memory and Allocations

- [ ] Allocation profiling run when allocator appears in hot path or RSS is high
- [ ] Allocation rate vs peak heap distinguished
- [ ] Large or frequent allocations tied to source lines
- [ ] Cache miss / page fault counters checked when CPU profile is inconclusive (`perf stat -d`)
- [ ] Container/object churn in managed/native hybrid code checked

## Phase 4 — I/O and Blocking

- [ ] Syscall summary captured when wall time >> CPU time (`strace -c`, `perf trace`)
- [ ] Sync disk I/O per operation identified
- [ ] Network round-trips and connection setup cost reviewed
- [ ] Lock contention investigated when threads are involved
- [ ] Blocking on external services quantified

## Phase 5 — Algorithm and Data Layout

- [ ] Scaling tested at multiple input sizes (1×, 10×, 100× when feasible)
- [ ] Asymptotic complexity matches observed scaling
- [ ] Unnecessary copies and temporaries identified in hot loops
- [ ] Data structure choice appropriate for access pattern
- [ ] Cache locality and struct layout considered for hot structures
- [ ] Repeated work (re-parse, re-hash, re-sort) eliminated or cached

## Phase 6 — Concurrency

- [ ] Thread/goroutine count vs CPU cores assessed
- [ ] Lock hold times and contention points identified
- [ ] False sharing checked for hot atomics/counters
- [ ] Work batching and queue depth reviewed
- [ ] Parallel speedup measured (strong vs weak scaling noted)

## Phase 7 — Report Quality

- [ ] Every finding has ID, severity, category, location, evidence, impact, recommendation
- [ ] Findings sorted by severity and estimated impact
- [ ] Optimization roadmap table included
- [ ] Recommendations tied to measurements (no unsupported micro-opts)
- [ ] Clean/efficient areas noted to prevent unnecessary changes
- [ ] Re-profile commands documented for verification

## Phase 8 — Implementation (when opted in)

- [ ] Fixes applied in priority order (Critical → High → Medium → Low)
- [ ] Same baseline workload re-run after each batch
- [ ] Before/after metrics updated in report
- [ ] Tests pass ([test](../test/SKILL.md))
- [ ] Lint/format clean ([lint](../lint/SKILL.md))
- [ ] No correctness regressions; memcheck considered after aggressive memory changes
- [ ] Benchmark or regression guard added when appropriate

## Build and Compiler Opportunities (apply when profile supports)

- [ ] Link-time optimization (`-flto`) trial on release build
- [ ] Profile-guided optimization (PGO) for stable hot paths
- [ ] `-march=native` or CPU-specific tuning for deployment target
- [ ] Auto-vectorization verified (`-Rpass-missed=.*`, `-fopt-info-vec`)
- [ ] Unneeded debug/assert stripped from release hot paths only when safe

## Red Flags — Investigate Immediately

- [ ] Busy loop or spin-wait consuming CPU
- [ ] O(n²) or worse on production-sized input
- [ ] Per-request full table scan or unindexed lookup
- [ ] Logging or string formatting inside innermost loop
- [ ] Mutex held across I/O
- [ ] Unbounded buffer growth without backpressure
- [ ] Single-threaded bottleneck on multi-core workload
