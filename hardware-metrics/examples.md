# Hardware Metrics — Examples

Adapt commands to the platform and hardware present. Prefer tools already installed; install only when needed and document what was added.

## Install Monitoring Tools

| Platform | Tools | Command |
|----------|-------|---------|
| Debian/Ubuntu | lm-sensors, htop, sysstat | `sudo apt-get install -y lm-sensors htop sysstat` |
| Debian/Ubuntu (NVIDIA) | nvidia-utils, nvtop | `sudo apt-get install -y nvidia-utils nvtop` |
| Fedora | lm_sensors, htop, sysstat | `sudo dnf install lm_sensors htop sysstat` |
| Arch | lm_sensors, htop, nvtop | `sudo pacman -S lm_sensors htop nvtop` |
| macOS | powermetrics (built-in) | Xcode CLT; `sudo powermetrics --help` |
| Windows | nvidia-smi (with driver) | Install NVIDIA/AMD driver; optional HWiNFO |

Initialize lm-sensors on Linux when `sensors` shows no chips:

```bash
sudo sensors-detect --auto
sensors
```

Verify: `sensors`, `nvidia-smi`, `htop --version`, `mpstat -V`

## Linux — Idle Snapshot

```bash
echo "=== CPU / load ==="
uptime
mpstat 1 3

echo "=== Memory ==="
free -h

echo "=== Temperatures ==="
sensors 2>/dev/null || grep -r . /sys/class/thermal/thermal_zone*/temp 2>/dev/null | head

echo "=== GPU ==="
nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw --format=csv 2>/dev/null || echo "no NVIDIA GPU"
```

## Linux — Monitor a Command

Run workload and sample the child process:

```bash
/usr/bin/time -v ./my-workload --args 2>&1 | tee workload-time.txt &
WPID=$!
pidstat -u -r -h -p "$WPID" 1 30
wait "$WPID"
```

Or sample system-wide while a command runs:

```bash
( while true; do date -Is; mpstat 1 1 | tail -1; free -h | awk '/Mem:/'; nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader 2>/dev/null; sleep 2; done ) &
MON=$!
./my-workload --args
kill "$MON" 2>/dev/null
```

## Linux — NVIDIA GPU Time Series

```bash
# 1 s interval: power, util, clocks, temp, mem
nvidia-smi dmon -s pucvmet -d 1 -c 120 -f gpu-metrics.csv
```

Check throttling and limits:

```bash
nvidia-smi -q -d PERFORMANCE,CLOCK,TEMPERATURE,POWER
```

Processes using the GPU:

```bash
nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv
```

## Linux — AMD GPU

```bash
rocm-smi --showuse --showmemuse --showtemp
# or interactive: radeontop
```

## Linux — Intel GPU

```bash
sudo intel_gpu_top -J -s 1000
# JSON samples every 1 s (requires intel-gpu-tools)
```

## Linux — Thermal Zones (no lm-sensors)

```bash
for z in /sys/class/thermal/thermal_zone*; do
  echo "$(basename "$z"): $(cat "$z/type" 2>/dev/null) $(($(cat "$z/temp") / 1000))°C"
done
```

## macOS

```bash
# CPU and memory snapshot
top -l 1 -s 0 | head -20
vm_stat

# CPU package / SMC sampling (requires sudo)
sudo powermetrics --samplers cpu_power -i 1000 -n 30

# Apple Silicon GPU/power (model-dependent)
sudo powermetrics --samplers gpu_power -i 1000 -n 30
```

Activity Monitor shows GPU history on supported Macs when the window is open.

## Windows (PowerShell)

```powershell
# CPU
Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 1 -MaxSamples 5

# Memory
Get-Counter '\Memory\Available MBytes' -SampleInterval 1 -MaxSamples 5

# NVIDIA
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv
```

## Docker / VM Caveats

- **Containers** without `--gpus all` (or equivalent) will not show GPU metrics inside the container.
- **Temperature sensors** may be hidden in VMs; use hypervisor/host metrics when guest `sensors` is empty.
- **WSL2** reports Linux memory through Windows host limits; GPU via WSL CUDA when configured.

Example GPU-enabled container check:

```bash
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

## Python One-Shot (when shell tools missing)

Use only when dedicated tools are unavailable:

```python
import psutil
print("CPU %:", psutil.cpu_percent(interval=1))
print("RAM:", psutil.virtual_memory()._asdict())
print("Per CPU:", psutil.cpu_percent(interval=1, percpu=True))
```

GPU still requires vendor tools (`nvidia-smi`, `pynvml`) — do not infer GPU util from CPU metrics alone.

## Correlating with Application Profiling

When hardware metrics show low utilization but slow runtime:

1. Note CPU/GPU/RAM headroom in this report
2. Switch to [compiled-performance](../compiled-performance/SKILL.md) or [interpreted-performance](../interpreted-performance/SKILL.md) for hot-path analysis
3. Re-run hardware metrics after fixes if saturation was near limits
