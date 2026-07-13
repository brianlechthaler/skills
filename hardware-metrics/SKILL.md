---
name: hardware-metrics
description: >-
  Measure system and hardware performance with CPU usage, RAM usage, GPU
  utilization, and hardware temperatures (CPU, GPU, and related sensors).
  Produce baseline snapshots, sustained-load samples, and structured reports
  with thermal and resource headroom analysis. Use when the user asks to
  monitor system resources, check CPU/RAM/GPU usage, measure temperatures,
  diagnose thermal throttling, or benchmark hardware utilization under load.
---

# Hardware Metrics

Measure **host-level resource utilization and thermal behavior** while a workload runs. Capture CPU, memory, GPU, and temperature metrics with comparable baselines, identify saturation or throttling, and report headroom with evidence.

This skill covers **system and hardware monitoring** — not application hot-path profiling. For code-level bottlenecks, use [compiled-performance](../compiled-performance/SKILL.md) or [interpreted-performance](../interpreted-performance/SKILL.md). For browser or web delivery metrics, use [web-performance](../web-performance/SKILL.md).

## When to Use

| Applies | Does not apply |
|---------|----------------|
| CPU, RAM, GPU, or temperature monitoring during a workload | Function-level profiling or flame graphs (use compiled/interpreted-performance) |
| Thermal throttling, overheating, or fan-noise investigation | Memory leak detection in C/C++ (use valgrind-memcheck) |
| Capacity planning: cores, RAM, VRAM, cooling headroom | Lighthouse, Core Web Vitals, bundle size (use web-performance) |
| Before/after hardware or config changes (power limits, drivers, cooling) | CI pipeline duration (use ci-optimize) |
| User asks for `nvidia-smi`, `sensors`, `htop`, resource usage, or temps | |

When unsure, default to **idle baseline → workload sample → sustained sample → temperature check**.

## Prerequisites

1. **Target workload defined** — command, service URL, benchmark, or process name/PID to observe
2. **Platform identified** — Linux, macOS, or Windows; bare metal vs VM vs container
3. **Monitoring tools available** — install or use container; see [examples.md](examples.md)
4. **Sampling interval chosen** — typically 1–5 s for interactive checks, 0.5–1 s under heavy GPU/CPU load

On Linux, verify basic access:

```bash
nproc
free -h
command -v sensors nvidia-smi nvtop 2>/dev/null
```

In containers or VMs, note that GPU passthrough and some temperature sensors may be unavailable or show host values only.

## Audit Workflow

Copy and track progress:

```
Hardware metrics audit:
- [ ] Phase 0: Recon — platform, hardware, workload, monitoring tools
- [ ] Phase 1: Idle baseline — CPU, RAM, GPU, temperatures
- [ ] Phase 2: Workload capture — same metrics under representative load
- [ ] Phase 3: Sustained load — time series, peaks, throttling signals
- [ ] Phase 4: Analysis — saturation, headroom, thermal limits
- [ ] Phase 5: Report — structured findings with evidence
```

Run phases **in order**. Do not claim saturation or throttling without sampled data.

### Phase 0 — Recon

Map what you can measure before sampling:

- OS and kernel (`uname -a`), bare metal vs VM vs WSL vs container
- CPU model and core/thread count (`lscpu`, `sysctl -n machdep.cpu.brand_string`, Windows `wmic cpu get name`)
- RAM installed (`free -h`, `system_profiler SPHardwareDataType`)
- GPU(s) present — NVIDIA, AMD, Intel (`lspci`, `nvidia-smi -L`, Activity Monitor)
- Workload: CLI command, service, game, training job, build, or PID
- Duration: burst (seconds), sustained (minutes+), or steady-state server load
- Existing monitoring: `htop`, `nvtop`, Prometheus, `nvidia-smi dmon`, vendor tools

Read project README or run scripts when the workload is an application in this repo. Identify the **metric the user cares about** (peak GPU%, RAM high-water, CPU package temp, etc.).

### Phase 1 — Idle Baseline

Sample the system **before** starting the workload (or with workload stopped). Record at least one snapshot; prefer 3 samples 5 s apart and report median.

**Record in the report:**

| Metric | Source | Idle value |
|--------|--------|------------|
| CPU usage (system %) | `top`, `mpstat`, `psutil` | |
| Per-core CPU % | `mpstat -P ALL`, `htop` | |
| Load average (1/5/15) | `uptime`, `/proc/loadavg` | |
| RAM used / available | `free -h`, `vm_stat` | |
| Swap used | `free -h`, `swapon --show` | |
| GPU utilization % | `nvidia-smi`, `nvtop`, `intel_gpu_top` | |
| GPU memory used / total | `nvidia-smi`, `rocm-smi` | |
| CPU temperature | `sensors`, `/sys/class/thermal`, `powermetrics` | |
| GPU temperature | `nvidia-smi`, `rocm-smi`, `sensors` | |
| Fan speeds (if available) | `sensors`, vendor tools | |

Note sensor labels (e.g. `Tctl`, `Package id 0`, `edge`, `junction`) — different platforms expose different names for CPU/GPU die temps.

### Phase 2 — Workload Capture

Run the **representative workload** and capture metrics during active work (not during startup/teardown only).

**Guidelines:**

- Start sampling **before** the workload; stop after it finishes or after a fixed window (e.g. 60 s steady state)
- For CLI jobs: wrap with `/usr/bin/time -v` when wall time and max RSS matter
- For servers: generate load (requests, users, batch jobs) then sample under steady traffic
- For GPU jobs: ensure the process uses the expected device (`CUDA_VISIBLE_DEVICES`, `--gpu`)

**Minimum capture set:**

| Metric | How |
|--------|-----|
| CPU % (process and system) | `pidstat -u`, `top -p PID`, `ps -o %cpu` |
| RAM (process RSS and system) | `pidstat -r`, `ps -o rss`, `smem -P` |
| GPU util and VRAM | `nvidia-smi --query-compute-apps=...`, `nvidia-smi dmon` |
| Temperatures | Same tools as Phase 1, sampled during load |

Prefer **multiple samples** over a single point-in-time reading.

### Phase 3 — Sustained Load

For workloads longer than ~30 s or when thermal behavior matters:

1. Sample every 1–5 s for the steady portion of the run
2. Record **peak** CPU%, RAM, GPU%, and temperatures
3. Watch for **throttling signals**:
   - CPU frequency drops under sustained load (`watch -n1 "grep MHz /proc/cpuinfo"`, `cpufreq-info`, `powermetrics`)
   - GPU clock or power limit throttling (`nvidia-smi -q -d CLOCK`, `THROTTLING` in `nvidia-smi`)
   - Temperature plateau at or above vendor limits (often ~80–100 °C CPU junction, ~83–90 °C GPU depending on card)
   - Rising swap use or OOM killer messages (`dmesg`, `journalctl -k`)

Use time-series tools when available: `nvidia-smi dmon`, `nvtop`, `sar`, or a short loop writing CSV for charting.

### Phase 4 — Analysis

Interpret measurements — do not list numbers without context.

| Signal | Likely meaning | Follow-up |
|--------|----------------|-----------|
| CPU ~100% on all cores, low GPU | CPU-bound workload | Profile app or add cores; check thermal headroom |
| GPU ~100%, low CPU | GPU-bound (ML, render, encode) | Check VRAM, power limit, cooling |
| RAM near total, swap growing | Memory pressure | Reduce footprint, add RAM, fix leak (see interpreted/compiled-performance) |
| High temp, declining clocks | Thermal or power throttling | Improve cooling, lower power limit, reduce load |
| Low util but slow workload | I/O, blocking, or wrong device | Use compiled/interpreted-performance for app profiling |
| VM shows flat or missing sensors | Hypervisor limits visibility | Run on host or use hypervisor metrics |

Compute **headroom** when useful:

- CPU: `(100% - sustained CPU%)` or cores idle under load
- RAM: `available` at peak vs `total`
- GPU: `(100% - sustained GPU util)` and free VRAM
- Thermal: margin to typical throttle point (document assumed limit)

### Phase 5 — Report

Deliver a structured report:

```markdown
# Hardware Metrics Report — <workload or system>

## Executive summary
<1–3 sentences: primary resource limit, thermal status, top recommendation>

## Environment
- Platform: `<OS, kernel, bare metal / VM / container>`
- CPU: `<model, cores/threads>`
- RAM: `<installed>`
- GPU: `<model, driver version if known>`
- Workload: `<command, duration, concurrency>`
- Tools: `<nvidia-smi, sensors, htop, …>`

## Baseline (idle)
| Metric | Value |
|--------|-------|
| CPU (system) | |
| RAM used / total | |
| GPU util / VRAM | |
| CPU temp | |
| GPU temp | |

## Under load
| Metric | Median | Peak |
|--------|--------|------|
| CPU (system / process) | | |
| RAM (system / process RSS) | | |
| GPU util / VRAM | | |
| CPU temp | | |
| GPU temp | | |

## Findings

### HW-001: <short title>
- **Severity**: Critical / High / Medium / Low
- **Category**: CPU / Memory / GPU / Thermal / Configuration
- **Evidence**: <sample output, time series, dmesg snippet>
- **Impact**: <e.g. thermal throttling after 90 s, 98% RAM with swap>
- **Recommendation**: <specific change — cooling, `-j`, smaller batch, device selection>
- **Headroom**: <quantified if applicable>

(repeat per finding)

## Clean areas
<sensors healthy, ample RAM, GPU underutilized with CPU bound — tie to next profiling step>

## Next steps
<re-sample command; correlate with app profile; hardware change to test>
```

Sort findings by severity. Tie recommendations to **measured values**, not guesses.

Full per-phase checklists: [checklist.md](checklist.md)

## Quick Reference — Default Commands

| Goal | Linux | macOS | Windows |
|------|-------|-------|---------|
| CPU + RAM snapshot | `top -bn1 \| head -20` | `top -l 1` | `Get-Counter '\Processor(_Total)\% Processor Time'` |
| Per-process CPU/RAM | `pidstat -u -r -p PID 1 5` | `ps -o pid,pcpu,rss -p PID` | Task Manager / `Get-Process` |
| GPU snapshot | `nvidia-smi` | Activity Monitor / `sudo powermetrics` | `nvidia-smi` |
| GPU time series | `nvidia-smi dmon -s pucvmet -d 1` | `sudo powermetrics --samplers gpu_power` | `nvidia-smi dmon` |
| Temperatures | `sensors` | `sudo powermetrics --samplers smc` | HWiNFO / `nvidia-smi -q -d TEMPERATURE` |
| Thermal zones (Linux) | `cat /sys/class/thermal/thermal_zone*/temp` | — | — |

Platform-specific recipes and install commands: [examples.md](examples.md)

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Single `top` glance during startup | Sample steady state; multiple intervals |
| Ignoring per-core vs aggregate CPU | Report both when relevant |
| Confusing GPU memory used with system RAM | Separate VRAM and RSS columns |
| Treating `Tctl` and junction temp as identical | Note sensor type and vendor docs |
| Measuring inside container without GPU passthrough | Confirm device visibility (`nvidia-smi` in container) |
| Recommending hardware upgrades without peak data | Show peak util and temp from sustained run |
| Replacing app profiling with hardware metrics only | Pair with compiled/interpreted-performance when code is slow but util is low |

## Additional Resources

- Platform commands and install: [examples.md](examples.md)
- Detailed audit checklists: [checklist.md](checklist.md)
- Application profiling after resource limit identified: [compiled-performance](../compiled-performance/SKILL.md), [interpreted-performance](../interpreted-performance/SKILL.md)
- Containerized runs: [docker](../docker/SKILL.md)
