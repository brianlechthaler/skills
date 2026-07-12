# Interpreted Performance Checklists

Reference for [SKILL.md](SKILL.md). Work through every applicable item — mark N/A only with evidence.

## Phase 0 — Recon

- [ ] Language, runtime version, and package manager identified
- [ ] Framework and server/worker model documented (sync, async, job queue)
- [ ] Entry command and typical args/config recorded
- [ ] Representative workload defined (route, script input, job payload, dataset size)
- [ ] Performance goal stated (p99 latency, throughput, memory cap, cold start)
- [ ] Existing benchmarks or load tests located
- [ ] Native extensions noted (NumPy, sharp, bcrypt, etc.)
- [ ] Dev-only overhead identified (debug mode, reload, verbose logging)

## Phase 1 — Baseline

- [ ] Workload run ≥3 times; median (or mean ± stdev) recorded
- [ ] Wall time or latency percentiles captured
- [ ] Throughput recorded when applicable (RPS, jobs/sec, rows/sec)
- [ ] Peak RSS or memory high-water mark recorded
- [ ] GC pause / allocation metrics captured when runtime exposes them
- [ ] Event-loop lag measured for Node/async apps when relevant
- [ ] Baseline table filled in report before any recommendations

## Phase 2 — CPU Profiling

- [ ] Correct profiler selected for stack (py-spy, clinic, stackprof, etc.)
- [ ] Profile captured under realistic load (not idle server)
- [ ] Top hot functions identified (≥5% samples or clear latency share)
- [ ] Application vs stdlib vs native extension time distinguished
- [ ] Call chains understood (not only leaf functions)
- [ ] Flame graph or equivalent produced when useful

## Phase 3 — Memory and GC

- [ ] Memory profiling run when RSS grows or GC appears in traces
- [ ] Allocation rate vs peak heap vs retained references distinguished
- [ ] Leak suspects tied to object types or call sites
- [ ] Unbounded caches, global lists, and closure retention checked
- [ ] Large object churn in hot loops identified

## Phase 4 — I/O and Blocking

- [ ] Database query count and slow queries reviewed under load
- [ ] N+1 ORM patterns identified
- [ ] Network call patterns reviewed (sequential vs parallel, timeouts)
- [ ] Sync I/O or blocking calls in async code identified
- [ ] Disk and logging volume on hot path quantified
- [ ] Connection pool sizing vs worker count reviewed

## Phase 5 — Algorithm and Libraries

- [ ] Scaling tested at multiple input sizes (1×, 10×, 100× when feasible)
- [ ] Asymptotic complexity matches observed scaling
- [ ] Data structure choice appropriate for access pattern
- [ ] Parsing/serialization cost on hot path measured
- [ ] Import-time and module-level side effects checked for cold start
- [ ] Vectorization or library swap considered when loops dominate numeric work

## Phase 6 — Concurrency

- [ ] Worker/process count vs CPU cores and DB pool assessed
- [ ] GIL / event-loop constraints understood for CPU-bound work
- [ ] Lock contention and shared mutable state reviewed
- [ ] Job queue depth, batching, and backpressure reviewed
- [ ] Parallel speedup measured; contention regressions noted

## Phase 7 — Report Quality

- [ ] Every finding has ID, severity, category, location, evidence, impact, recommendation
- [ ] Findings sorted by severity and estimated impact
- [ ] Optimization roadmap table included
- [ ] Recommendations tied to measurements (no unsupported micro-opts)
- [ ] Clean/efficient areas noted to prevent unnecessary changes
- [ ] Re-profile and load-test commands documented for verification

## Phase 8 — Implementation (when opted in)

- [ ] Fixes applied in priority order (Critical → High → Medium → Low)
- [ ] Same baseline workload re-run after each batch
- [ ] Before/after metrics updated in report
- [ ] Tests pass ([test](../test/SKILL.md))
- [ ] Lint/format clean ([lint](../lint/SKILL.md))
- [ ] No correctness regressions under load
- [ ] Benchmark or regression guard added when appropriate

## Runtime-Specific Opportunities (apply when profile supports)

- [ ] Python: `__slots__`, generators, `lru_cache` with bounds, multiprocessing for CPU-bound
- [ ] Python: ORM `select_related` / `prefetch_related`, raw SQL for proven hot queries
- [ ] Node: worker threads / worker pool for CPU work; streams for large payloads
- [ ] Node: avoid sync fs/crypto on request path
- [ ] Ruby: `pluck` vs loading AR objects, `includes`/`preload`, frozen string literals where applicable
- [ ] PHP: OPcache enabled in prod-like run; xhprof hot paths addressed
- [ ] General: connection pooling, HTTP keep-alive, batch API calls

## Red Flags — Investigate Immediately

- [ ] N+1 queries on user-facing route
- [ ] Unindexed filter/sort on large table
- [ ] Loading entire table or file into memory per request
- [ ] O(n²) loop or repeated linear search on growing data
- [ ] Blocking call inside async handler or event loop
- [ ] Unbounded in-memory cache or job retry queue
- [ ] Logging full payloads or debug SQL in production path
- [ ] Worker count increased without fixing DB/query bottleneck
