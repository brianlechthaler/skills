# Compiled Performance — Examples

Adapt paths and build commands to the project. Prefer existing Makefile/CMake/Cargo targets when present.

## Install Profilers

| Platform | Tools | Command |
|----------|-------|---------|
| Debian/Ubuntu | perf, hyperfine, heaptrack | `sudo apt-get install -y linux-tools-generic hyperfine heaptrack` |
| Fedora | perf, hyperfine | `sudo dnf install perf hyperfine` |
| Arch | perf, hyperfine, heaptrack | `sudo pacman -S perf hyperfine heaptrack` |
| macOS | sample, Instruments | Xcode Command Line Tools (`xcode-select --install`) |
| Go | pprof (stdlib) | Included with Go toolchain |
| Rust | flamegraph, samply | `cargo install flamegraph` / `cargo install samply` |

Verify: `perf --version`, `hyperfine --version`, `go version`, `cargo --version`

## Docker (no host install)

When `sudo` or package install is unavailable:

```bash
docker run --rm -v "$(pwd):/work" -w /work --cap-add SYS_PTRACE \
  ubuntu:24.04 bash -c '
  apt-get update -qq && apt-get install -y -qq build-essential linux-tools-generic hyperfine
  make CFLAGS="-g -O2" myprog
  hyperfine --warmup 2 "./myprog --input data/sample.dat"
'
```

For `perf record`, the container may need `--privileged` or `kernel.perf_event_paranoid` adjusted on the host.

## C / C++ — CMake

```bash
cmake -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build -j
hyperfine --warmup 3 './build/myapp --input benchmark.dat'

perf record -g --call-graph dwarf -F 997 -- ./build/myapp --input benchmark.dat
perf report --stdio | head -60
```

With Google Benchmark:

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_BENCHMARKS=ON
cmake --build build --target benchmark_all
./build/benchmarks/all --benchmark_min_time=1s
```

## C / C++ — Make

```bash
make CFLAGS="-g -O2" myprog
/usr/bin/time -v ./myprog args 2>&1 | tee baseline.txt

heaptrack ./myprog args
# Opens heaptrack.myprog.*.gz — summarize with heaptrack_print
```

## Valgrind Callgrind (cache / call counts)

Slower than `perf` but needs no special permissions:

```bash
valgrind --tool=callgrind --callgrind-out-file=callgrind.out ./myapp args
callgrind_annotate callgrind.out | head -40
# Visualize with kcachegrind or QCachegrind
```

## Go

```bash
go test -bench=. -benchmem -count=5 ./...
go test -bench=BenchmarkFoo -cpuprofile=cpu.prof -memprofile=mem.prof ./pkg/...
go tool pprof -top cpu.prof
go tool pprof -top -alloc_space mem.prof
```

Trace scheduler and blocking:

```bash
go test -trace=trace.out ./...
go tool trace trace.out
```

## Rust

```bash
cargo build --release
hyperfine --warmup 3 './target/release/mybin -- input'

# Flamegraph (Linux, perf available)
cargo install flamegraph
cargo flamegraph --bin mybin -- -- input

# Criterion benches
cargo bench
```

Optional release profile with debug symbols in `Cargo.toml`:

```toml
[profile.release]
debug = true
```

## macOS — sample

```bash
make CFLAGS="-g -O2" myprog
/sample $(pgrep myprog) 10 -f
# Or launch under sample:
sample ./myprog 10 -f
```

For deeper analysis, use Instruments → Time Profiler from Xcode.

## Java — async-profiler

```bash
# Attach to running JVM
async-profiler -d 30 -f profile.html <pid>
```

Or enable JFR in the JVM and analyze with JDK Mission Control.

## .NET

```bash
dotnet-trace collect --process-id <pid> --profile cpu-sampling
dotnet-counters monitor --process-id <pid> System.Runtime
```

## Interpreters with Native Extensions

When the bottleneck is in C/Rust extensions (Python, Ruby, Node):

1. Profile the **native** shared library with `perf record` on the process
2. Or use language-specific tools (`py-spy`, `rbspy`, `0x`) for mixed stacks
3. Rebuild the extension with `-g -O2` before native profiling

## Regression Guard — Add a Benchmark

After implementing a fix, add or extend a benchmark so CI can catch regressions:

| Stack | Pattern |
|-------|---------|
| Go | `func BenchmarkFoo(b *testing.B)` in `*_test.go` |
| Rust | Criterion bench in `benches/` |
| C++ | Google Benchmark `BENCHMARK(BM_Foo)` |
| Generic | Script invoking `hyperfine` with threshold in CI (optional) |

Keep benchmarks **representative** but bounded (fixed input size, iteration cap) so CI stays fast.
