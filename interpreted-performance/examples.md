# Interpreted Performance — Examples

Adapt paths and commands to the project. Prefer existing Makefile/npm/poetry targets when present.

## Install Profilers

| Platform | Tools | Command |
|----------|-------|---------|
| Debian/Ubuntu | hyperfine, py-spy | `sudo apt-get install -y hyperfine`; `pip install py-spy scalene memray` |
| macOS | hyperfine, py-spy | `brew install hyperfine`; `pip install py-spy` |
| Node.js | clinic, 0x | `npm i -g clinic 0x` |
| Ruby | stackprof, memory_profiler | `gem install stackprof memory_profiler` |
| PHP | Xdebug | `pecl install xdebug` or distro package |

Verify: `hyperfine --version`, `python --version`, `node --version`, `ruby --version`

## Docker (no host install)

```bash
docker run --rm -v "$(pwd):/work" -w /work python:3.12-slim bash -c '
  pip install -q py-spy hyperfine
  hyperfine --warmup 2 "python script.py --input data/sample.json"
'
```

For Node:

```bash
docker run --rm -v "$(pwd):/work" -w /work node:22-slim bash -c '
  npm ci --omit=dev
  npx hyperfine --warmup 2 "node server.js"
'
```

## Python — CLI / script

```bash
hyperfine --warmup 3 --min-runs 5 'python script.py --input data.json'

# Sampling profiler (no code changes; works on running process)
py-spy record -o profile.svg -- python script.py --input data.json
py-spy top -- python script.py

# Deterministic (adds overhead)
python -m cProfile -o profile.stats script.py
python -m pstats -s cumtime profile.stats  # interactive: sort cumtime, head 30

# Line-level (requires @profile decorators / kernprof)
pip install line_profiler
kernprof -l -v script.py

# Memory over time
python -m memory_profiler script.py
python -c "
import tracemalloc
tracemalloc.start()
# ... run workload ...
snap = tracemalloc.take_snapshot()
for stat in snap.statistics('lineno')[:15]:
    print(stat)
"
```

## Python — FastAPI / Django / Flask

Start the server, then profile under load:

```bash
# Terminal 1
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — sample running workers
py-spy record -o api.svg --pid $(pgrep -f 'uvicorn app.main')

# Load (pick one)
npx autocannon -c 10 -d 30 http://127.0.0.1:8000/api/items
wrk -t4 -c32 -d30s http://127.0.0.1:8000/api/items
```

Enable Django query logging or `django-debug-toolbar` in dev to catch N+1 before production profiling.

Pytest benchmark:

```bash
pip install pytest-benchmark
pytest tests/bench/ --benchmark-only --benchmark-min-rounds=5
```

## Node.js — HTTP server

```bash
hyperfine --warmup 2 'node server.js'  # short-lived; prefer load test for servers

# Flame graph (development)
clinic flame -- node server.js
# Follow prompts; reproduce load in another terminal

# Built-in CPU profile
node --cpu-prof server.js
node --prof-process isolate-*.log > processed.txt

# Event-loop delay
node -e "
const { monitorEventLoopDelay } = require('perf_hooks');
const h = monitorEventLoopDelay(); h.enable();
setTimeout(() => { console.log(h); h.disable(); }, 10000);
"
```

Load test:

```bash
npx autocannon -c 20 -d 30 http://127.0.0.1:3000/health
```

## Ruby — Rails / script

```bash
# Stackprof in code or middleware
STACKPROF=1 stackprof tmp/stackprof-cpu-*.dump

# Benchmark gem
ruby -Ilib -rbenchmark benchmark/workload.rb

# Memory
derailed bundle:mem  # Rails gem bloat
bundle exec ruby -rmemory_profiler -e "MemoryProfiler.report { load 'script.rb' }.pretty_print"
```

## PHP

```bash
# XHProf (when extension available)
php -d xhprof.enable=1 script.php
# Analyze xhprof.out.* with xhprof viewer

# Built-in timing
/usr/bin/time -v php public/index.php
```

## Perl

```bash
perl -d:NYTProf script.pl
nytprofhtml --out nytprof
# Open nytprof/index.html
```

## Lua / LuaJIT

```lua
-- LuaJIT
local prof = require "jit.p"
prof.start("fl", "profile.txt")
-- workload
prof.stop()
```

## HTTP load testing (any stack)

| Tool | Example |
|------|---------|
| wrk | `wrk -t4 -c64 -d30s --latency http://localhost:8080/` |
| autocannon | `autocannon -c 20 -d 30 http://localhost:8080/` |
| k6 | `k6 run --vus 20 --duration 30s load.js` |
| locust | `locust -f locustfile.py --headless -u 50 -r 5 -t 30s` |

Record **p50/p95/p99** and error rate, not only requests/sec.

## Native extensions in interpreted apps

When profiles show time in `.so` / `.pyd` / `libv8` / `numpy`:

1. Confirm with mixed-stack profiler (`py-spy`, `rbspy`, `perf record -p PID`)
2. If app Python/JS is just calling heavy native work, optimize **usage** (smaller dtypes, batch calls, avoid conversions)
3. For custom C/Rust extensions, use [compiled-performance](../compiled-performance/SKILL.md)

## Regression guard — add a benchmark

After implementing a fix:

| Stack | Pattern |
|-------|---------|
| Python | `pytest-benchmark` test or `hyperfine` in CI with threshold |
| Node | `benchmark` in test file or dedicated `bench/*.js` |
| Ruby | `Benchmark.bmbm` or Minitest benchmark helper |
| Generic | k6/locust smoke with latency assertion |

Keep benchmarks **representative** but bounded so CI stays fast.
