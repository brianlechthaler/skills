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

Verify: `sensors`, `nvidia-smi`, `htop --version`, `mpstat -V`, `iostat -V`

## Linux — Idle Snapshot

```bash
echo "=== CPU / load ==="
uptime
mpstat 1 3

echo "=== Memory ==="
free -h

echo "=== Disk layout ==="
lsblk -o NAME,MODEL,ROTA,SIZE,MOUNTPOINT 2>/dev/null || df -h

echo "=== Disk I/O ==="
iostat -xz 1 3 2>/dev/null || echo "install sysstat for iostat"

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
( while true; do date -Is; mpstat 1 1 | tail -1; free -h | awk '/Mem:/'; iostat -xz 1 1 2>/dev/null | awk 'NR>3 && $1 !~ /^(Device|loop)/ {print}'; nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader 2>/dev/null; sleep 2; done ) &
MON=$!
./my-workload --args
kill "$MON" 2>/dev/null
```

## Linux — Disk I/O Profiling

Identify devices and whether they are rotational (HDD) or SSD/NVMe (`ROTA=0`):

```bash
lsblk -o NAME,MODEL,ROTA,SIZE,MOUNTPOINT
df -h
```

Idle or under-load snapshot — extended stats per device (`-x` omit idle, `-z` omit zero-activity):

```bash
# Columns: r/s w/s rkB/s wkB/s await r_await w_await %util
iostat -xz 1 10
```

Per-process disk I/O (requires root or `CAP_SYS_ADMIN`):

```bash
sudo iotop -o -b -n 30 -d 1
# or for a specific PID:
pidstat -d -p PID 1 30
```

Time series to CSV for sustained runs:

```bash
iostat -xz 1 120 > disk-metrics.txt
```

Sustained disk benchmark (optional — measures raw device throughput, not workload I/O):

```bash
# Quick sequential read test on a spare file (adjust path and size)
fio --name=seqread --filename=/tmp/fio-test --size=1G --bs=1M --rw=read --iodepth=32 --direct=1 --numjobs=1

# Mixed random read/write — closer to database workloads
fio --name=randrw --filename=/tmp/fio-test --size=1G --bs=4k --rw=randrw --rwmixread=70 --iodepth=16 --direct=1 --numjobs=4 --runtime=30 --time_based
```

Remove test files after benchmarking. Do not run destructive `fio` tests on production data volumes without explicit approval.

Interpret key `iostat` fields:

| Field | Meaning | Saturation signal |
|-------|---------|-------------------|
| `rkB/s`, `wkB/s` | Read/write throughput | Compare to device spec or baseline |
| `r/s`, `w/s` | IOPS | High on HDD with small random writes |
| `%util` | Device busy time | Near 100% = saturated |
| `await` | Average I/O wait (ms) | Rising under load = latency pressure |
| `avgqu-sz` | Average queue depth | Sustained > 1 on single queue device |

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

# Disk I/O (requires iostat from optional Xcode CLT or third-party tools)
iostat -d 1 5 2>/dev/null || diskutil info disk0 | grep -E 'Device|Protocol|Solid State'

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

# Disk I/O
Get-Counter '\PhysicalDisk(*)\Disk Reads/sec','\PhysicalDisk(*)\Disk Writes/sec','\PhysicalDisk(*)\% Disk Time','\PhysicalDisk(*)\Avg. Disk sec/Read','\PhysicalDisk(*)\Avg. Disk sec/Write' -SampleInterval 1 -MaxSamples 5

# NVIDIA
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv
```

## Docker / VM Caveats

- **Containers** without `--gpus all` (or equivalent) will not show GPU metrics inside the container.
- **Temperature sensors** may be hidden in VMs; use hypervisor/host metrics when guest `sensors` is empty.
- **Disk metrics** in containers often reflect the host block device or overlay filesystem — confirm which mount path the workload uses (`df -h`, `mount`).
- **WSL2** reports Linux memory through Windows host limits; GPU via WSL CUDA when configured; disk I/O may reflect the Windows backing VHD.

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

When hardware metrics show low CPU/GPU utilization but slow runtime:

1. Check disk `%util` and `await` — disk saturation is a common cause of low CPU with slow wall time
2. Note CPU/GPU/RAM/disk headroom in this report
3. Switch to [compiled-performance](../compiled-performance/SKILL.md) or [interpreted-performance](../interpreted-performance/SKILL.md) for hot-path and per-syscall I/O analysis
4. Re-run hardware metrics after fixes if saturation was near limits
