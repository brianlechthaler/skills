# Valgrind Memcheck — Examples

Adapt paths and build commands to the project. Prefer Makefile/CMake targets when present.

## Install Valgrind

| Platform | Command |
|----------|---------|
| Debian/Ubuntu | `sudo apt-get update && sudo apt-get install -y valgrind` |
| Fedora/RHEL | `sudo dnf install valgrind` |
| Arch | `sudo pacman -S valgrind` |
| macOS (Intel) | `brew install valgrind` |

Verify: `valgrind --version`

## Docker (no host install)

When `sudo` or package install is unavailable, use a minimal Ubuntu container:

```bash
docker run --rm -v "$(pwd):/work" -w /work ubuntu:24.04 bash -c '
  apt-get update -qq && apt-get install -y -qq gcc valgrind
  gcc -g -O0 -o myprog src/*.c
  valgrind --leak-check=full ./myprog
'
```

Mount only the project directory; do not bake secrets into images.

## CMake

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
valgrind --leak-check=full --show-leak-kinds=all ./build/myapp
```

For tests:

```bash
valgrind --leak-check=full --error-exitcode=1 ctest --test-dir build --output-on-failure
# or run one test binary directly:
valgrind --leak-check=full ./build/tests/my_test
```

## Make

```bash
make CFLAGS="-g -O0" myprog
valgrind --leak-check=full ./myprog
```

## Catch test / Google Test

Run the test executable under Valgrind, not the test runner wrapper when possible:

```bash
valgrind --leak-check=full ./build/unit_tests --gtest_filter=MySuite.*
```

Use `--error-exitcode=1` in CI so Memcheck failures fail the job.

## Save log for reporting

```bash
valgrind \
  --leak-check=full \
  --show-leak-kinds=all \
  --track-origins=yes \
  --log-file=memcheck-$(date +%Y%m%d-%H%M%S).log \
  ./myprog "$@"
```

Parse the log file when building the detailed report.

## Suppressions (third-party noise only)

When library code produces known-benign reports you cannot fix:

```bash
valgrind --suppressions=valgrind.supp --leak-check=full ./myprog
```

Document each suppression in the report. Do not suppress definite leaks in project code.

## CI snippet (GitHub Actions)

```yaml
- name: Memcheck
  run: |
    sudo apt-get install -y valgrind
    cmake -B build -DCMAKE_BUILD_TYPE=Debug
    cmake --build build
    valgrind --leak-check=full --error-exitcode=1 ./build/myapp --help
```

Scope CI Memcheck to fast smoke binaries; full suites may need nightly jobs.
