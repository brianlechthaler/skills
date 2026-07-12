---
name: interpreted-performance
description: >-
  Analyze interpreted language application performance thoroughly with profilers
  and benchmarks, identify bottlenecks in CPU, memory, I/O, GC, and concurrency,
  suggest prioritized optimizations, and optionally implement fixes with
  before/after measurements. Use when the user asks to profile, benchmark,
  optimize, or speed up Python, JavaScript, Node.js, Ruby, PHP, Perl, Lua, or
  other dynamic/interpreted runtimes.
---

# Interpreted Performance

Conduct a **thorough, measured performance audit** of interpreted and dynamic-language applications. Baseline wall-clock and resource metrics first, profile hot paths with the right runtime tools, rank optimizations by impact × effort, and optionally implement them with verified gains.

This skill covers **Python, JavaScript/Node.js, Ruby, PHP, Perl, Lua**, and similar runtimes — including mixed stacks where hot paths live in C/Rust extensions. For native binaries and AOT/JIT-compiled targets (C/C++, Rust, Go), use [compiled-performance](../compiled-performance/SKILL.md). For browser page load and Core Web Vitals, use [web-performance](../web-performance/SKILL.md). For CI pipeline duration, use [ci-optimize](../ci-optimize/SKILL.md).

## When to Use

| Applies | Does not apply |
|---------|----------------|
| Python, Ruby, PHP, Perl, Lua apps, scripts, APIs, workers | Pure native binaries without a language runtime (use compiled-performance) |
| Node.js servers, CLIs, bundlers, serverless handlers | Browser bundle size / Lighthouse (use web-performance) |
| Django, Flask, FastAPI, Rails, Sinatra, Laravel, Express, etc. | GitHub Actions wall-clock (use ci-optimize) |
| Slow requests, high CPU/RSS, GC pauses, event-loop lag | C/C++ heap corruption (use valgrind-memcheck on extensions) |
| User asks to profile, benchmark, optimize, or "make it faster" | |

When unsure, default to **baseline + CPU profile + allocation/GC profile** before recommending changes.

## Implement Mode (decide first)

| User intent | Behavior after audit |
|-------------|----------------------|
| Default — "analyze performance", "profile this app", "find bottlenecks" | Deliver findings and recommendations, then **ask** whether to implement optimizations |
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

1. **Runnable entry point** — script, module, server start command, test/benchmark target
2. **Representative workload** — fixed input, request pattern, or benchmark harness so numbers are comparable
3. **Runtime and deps available** — correct language version, virtualenv/node_modules/bundle installed
4. **Profiler tooling** — install or use container; see [examples.md](examples.md)

Profile in an environment **close to production** (same runtime version, similar data size). Note dev-only overhead (debug mode, hot reload, verbose logging) in the report.

## Audit Workflow

Copy and track progress:

```
Interpreted performance audit:
- [ ] Phase 0: Recon — language, framework, entry points, workload
- [ ] Phase 1: Baseline — wall time, CPU, memory, throughput, GC/event-loop
- [ ] Phase 2: CPU profiling — hot functions, call stacks, flame graph
- [ ] Phase 3: Memory and GC — allocations, peak RSS, object churn
- [ ] Phase 4: I/O and blocking — DB, network, disk, sync calls in async code
- [ ] Phase 5: Algorithm and libraries — complexity, N+1, wrong data structures
- [ ] Phase 6: Concurrency — GIL, thread pools, event loop, worker saturation
- [ ] Phase 7: Report — prioritized findings with evidence and estimates
- [ ] Phase 8: Implement — prompt or auto-fix
```

Run phases **in order**. Do not recommend fixes without measurements for the affected area.

### Phase 0 — Recon

Map the performance surface before profiling:

- Language, runtime version, package manager (pip/poetry, npm/pnpm, bundler, composer)
- Framework (Django, FastAPI, Rails, Express, etc.) and process model (sync workers, async, Sidekiq/Celery)
- Entry command: `python app.py`, `uvicorn`, `node server.js`, `rails server`, `php-fpm`
- Representative workload: HTTP route, CLI args, job payload, dataset size
- Existing benchmarks (`pytest-benchmark`, `benchmark` gem, `hyperfine`, k6, locust)
- Deployment constraints: latency p99 vs throughput, memory cap, cold start
- Native extensions (NumPy, pandas, bcrypt, sharp) — note when CPU may be in C/Rust code

Read manifests (`pyproject.toml`, `package.json`, `Gemfile`, `composer.json`) and README. Identify the **critical path** the user cares about.

### Phase 1 — Baseline

Measure **before** proposing fixes. Run the workload at least **3 times**; report median (or mean ± stdev if variance is high).

**Record in the report:**

| Metric | Command / source | Value |
|--------|------------------|-------|
| Wall time | `hyperfine`, `time`, framework benchmark | |
| Throughput | req/sec, jobs/sec, rows/sec | |
| CPU (process %) | `top`, `ps`, profiler summary | |
| Peak RSS | `/usr/bin/time -v`, `ps`, runtime metrics | |
| GC / allocator | GC pause time, allocation rate (runtime-specific) | |
| Event-loop lag (Node) | `perf_hooks`, clinic.js | |
| p95/p99 latency (HTTP) | wrk, autocannon, k6, ab | |

Prefer [hyperfine](https://github.com/sharkdp/hyperfine) for CLI scripts:

```bash
hyperfine --warmup 3 --min-runs 5 'python script.py --input data.json'
```

For HTTP services, load with a fixed concurrency and duration; record latency percentiles, not just RPS.

Use the project's existing benchmark target when present (`pytest --benchmark-only`, `npm test -- --bench`, `ruby -Ilib benchmark/foo.rb`).

### Phase 2 — CPU Profiling

Pick the **default tool for the stack** (sampling preferred in production-like runs):

| Stack | Default tool | Deeper options |
|-------|--------------|----------------|
| Python | `py-spy`, `scalene` | `cProfile`/`snakeviz`, `pyinstrument`, `line_profiler` |
| Node.js | `clinic flame`, `0x` | `--cpu-prof`, `perf` on the process (Linux) |
| Ruby | `stackprof`, `ruby-prof` | `rbspy`, `memory_profiler` |
| PHP | Xdebug/XHProf mode | Blackfire, Tideways |
| Perl | `Devel::NYTProf` | `Devel::FastProf` |
| Lua | `lua-profiler`, `jit.p` (LuaJIT) | |

Read the profile **top-down**: identify functions accounting for ≥5% of samples (or the user's stated SLO gap). Distinguish **application code** from framework/stdlib and from **native extension** time.

When native code dominates, profile extensions with [compiled-performance](../compiled-performance/SKILL.md) techniques or use mixed-stack profilers (`py-spy`, `rbspy`, `perf` on PID).

### Phase 3 — Memory and GC

When RSS grows, GC pauses matter, or allocation rate is high:

| Stack | Tools |
|-------|-------|
| Python | `tracemalloc`, `memray`, `memory_profiler`, `gc` stats, `objgraph` |
| Node.js | `--heap-prof`, `clinic heapprofiler`, `node --inspect` heap snapshot |
| Ruby | `memory_profiler`, `derailed_benchmarks`, `stackprof` with `:memory` |
| PHP | Xdebug memory mode, `memory_get_usage()` instrumentation |
| General | `ps` RSS over time under sustained load |

Distinguish **allocation rate** vs **peak footprint** vs **retained references** (leaks). Recommend caching, generators, `__slots__`, streaming I/O, or weak refs only when data supports it.

### Phase 4 — I/O and Blocking

When CPU profile is flat but wall time or latency is high:

- **Database**: N+1 queries, missing indexes, row-by-row fetch vs batch, connection pool exhaustion
- **Network**: sequential HTTP calls, no timeout/retry budget, DNS on hot path
- **Disk**: sync reads/writes per request, unbuffered I/O, logging volume
- **Blocking in async**: sync ORM/requests inside `async def`, `time.sleep` in event loop
- **External services**: unbounded fan-out, no circuit breaker, cold connection per call

Use ORM/query logging, APM traces, or `strace -c` on the process when syscall overhead is suspected.

### Phase 5 — Algorithm and Libraries

Code review guided by profile evidence:

- Time complexity vs input size (measure at 1×, 10×, 100× scale)
- Wrong data structure (list vs set/dict, repeated linear search)
- Parsing/serialization in hot path (JSON, YAML, regex on large strings)
- ORM overhead vs raw SQL for proven hot queries
- Import-time cost and module-level side effects
- Python: use vectorized NumPy/pandas when loops dominate numeric work
- JS: avoid sync crypto/hash on large payloads in the request path

### Phase 6 — Concurrency

When using threads, processes, async, or job queues:

- **Python GIL**: CPU-bound work in threads won't parallelize — use `multiprocessing`, C extensions, or offload
- **Node**: single-threaded event loop — offload CPU work to worker threads / child processes
- **Worker count**: gunicorn/uvicorn workers vs CPU cores; Sidekiq/Celery concurrency vs DB pool size
- **Lock contention**: shared caches, global dicts, file locks
- **Queue depth**: backpressure, batching, idempotency under load

Measure parallel speedup; note when adding workers only increases DB contention.

### Phase 7 — Report

Deliver a structured report. For large audits with many findings, use the [canvas](../canvas/SKILL.md) skill for interactive layout.

```markdown
# Interpreted Performance Report — <app or component>

## Executive summary
<1–3 sentences: primary bottleneck, estimated headroom, top recommendation>

## Environment
- Runtime: `<language + version>`
- Entry: `<command>`
- Workload: `<route, script args, job payload>`
- Platform: `<OS, CPU, workers>`
- Tools: `<py-spy, hyperfine, …>`

## Baseline
| Metric | Before |
|--------|--------|
| Wall time / p99 latency | |
| Throughput | |
| Peak RSS | |
| GC / alloc rate | |

## Hot path (CPU)
<top 5–10 functions with % samples; note app vs stdlib vs native>

## Findings

### PERF-001: <short title>
- **Severity**: Critical / High / Medium / Low
- **Category**: CPU / Memory / I/O / Algorithm / Concurrency / Runtime
- **Location**: `<file>:<line>` or `<function>`
- **Evidence**: <profile snippet, query log, benchmark delta>
- **Impact**: <expected gain — e.g. "~60% p99 on /api/search">
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
<re-profile command; benchmark to add; load test to run>
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
| Hot DB/ORM functions | N+1 queries | `select_related`/`prefetch`, eager load, batch query |
| High RSS over time | Unbounded cache or leak | TTL, weak refs, stream and discard |
| Flat CPU, slow requests | I/O or blocking | Parallel fetch, async I/O, connection pooling |
| Python loop over big array | Interpreted loop | NumPy vectorization, C extension, `numba` |
| Node event-loop lag | Sync CPU or I/O on main thread | Worker thread, split job, streaming |
| Scales poorly with N | O(n²) or repeated scan | Set/dict index, sort once, pagination |
| Slow cold start | Heavy imports | Lazy import, slimmer deps, startup profiler |
| Many workers, same DB limit | Pool exhaustion | Right-size workers, PgBouncer, query tuning |

Stack-specific commands and recipes: [examples.md](examples.md)

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Optimizing without baseline | Measure first; keep numbers in the report |
| Micro-optimizing cold paths | Focus on ≥5% sample share or measured latency share |
| Premature caching | Fix N+1 and algorithm first; cache with TTL and bounds |
| Adding workers without measuring DB | Profile query load and pool size first |
| Single-run timings | Multiple runs; report median |
| Profiling only "hello world" | Use production-like data volume and concurrency |
| Replacing interpreter with rewrite | Exhaust measured fixes in the current stack first unless rewrite requested |

## Additional Resources

- Stack-specific profiling recipes: [examples.md](examples.md)
- Detailed audit checklists: [checklist.md](checklist.md)
- Native extension hot paths: [compiled-performance](../compiled-performance/SKILL.md)
- Containerized profiling (no host install): [docker](../docker/SKILL.md)
