# Hardware Metrics Checklists

Reference for [SKILL.md](SKILL.md). Work through every applicable item — mark N/A only with evidence.

## Phase 0 — Recon

- [ ] OS, kernel, and environment type documented (bare metal / VM / container / WSL)
- [ ] CPU model and logical core count recorded
- [ ] Installed RAM recorded
- [ ] GPU vendor and model identified (or confirmed absent)
- [ ] Workload command, duration, and concurrency documented
- [ ] Monitoring tools verified (`sensors`, `nvidia-smi`, `htop`, etc.)
- [ ] Primary metric of interest stated (peak GPU%, RAM, CPU temp, etc.)

## Phase 1 — Idle Baseline

- [ ] At least one idle snapshot taken (prefer 3 samples, median reported)
- [ ] System CPU usage recorded
- [ ] Load average recorded
- [ ] RAM used / available and swap use recorded
- [ ] GPU util and VRAM recorded (or N/A with evidence)
- [ ] CPU temperature recorded with sensor label
- [ ] GPU temperature recorded with sensor label (or N/A)
- [ ] Idle baseline table filled before workload run

## Phase 2 — Workload Capture

- [ ] Workload is representative (not trivial hello-world unless requested)
- [ ] Sampling started during active work, not only startup/shutdown
- [ ] Process-level CPU and RSS captured when a specific PID exists
- [ ] System-level CPU and RAM captured under load
- [ ] GPU util and VRAM captured under load (or N/A)
- [ ] Temperatures sampled during load
- [ ] Multiple samples taken (not a single point-in-time only)

## Phase 3 — Sustained Load

- [ ] Steady-state window identified for runs longer than ~30 s
- [ ] Time series or repeated samples over steady state captured
- [ ] Peak CPU, RAM, GPU util, and temperatures recorded
- [ ] Throttling signals checked (clock drops, `nvidia-smi` perf state, thermal plateau)
- [ ] Swap growth or OOM/kernel messages checked when RAM is high

## Phase 4 — Analysis

- [ ] Primary bottleneck classified (CPU / memory / GPU / thermal / I/O suspicion)
- [ ] Headroom quantified where useful
- [ ] Sensor types interpreted (not raw numbers only)
- [ ] Container/VM limitations noted when sensors or GPU missing
- [ ] Cross-reference to app profiling when util is low but workload is slow

## Phase 5 — Report

- [ ] Executive summary states limit and recommendation
- [ ] Environment section complete
- [ ] Idle and under-load tables filled
- [ ] Findings use HW-### IDs with severity and evidence
- [ ] Recommendations tied to measured peaks/medians
- [ ] Next steps include exact re-sample commands
