---
name: hardware-requirements
description: >-
  Infer and document hardware requirements for a project — CPU, RAM, disk, GPU,
  OS, and network — from stack signals and workload type. Suggest minimum and
  recommended specs, then ask whether to add them to project documentation.
  Use when the user asks for system requirements, hardware requirements, what
  machine is needed to run or develop the project, or to document specs in the
  README or docs.
---

# Hardware Requirements

Suggest **minimum and recommended hardware** so people know what machine can build, run, or develop this project. Base specs on **project evidence** (deps, docs, Docker, CI, workload type) — not guesswork or generic "8 GB RAM" defaults.

This skill **prescribes** sizing for a project. To **measure** a live machine under load, use [hardware-metrics](../hardware-metrics/SKILL.md). For local LLM model fit on detected hardware, use [llmfit](../llmfit/SKILL.md).

## Core Rules

1. **Evidence first** — map stack and workload from the repo before naming numbers.
2. **Minimum vs recommended** — always give both tiers; say what each tier supports.
3. **Separate contexts** — distinguish **dev/build**, **local run**, and **production/server** when they diverge.
4. **Ask before writing docs** — present the suggestion, then ask if the user wants it added to documentation. Do not edit README/`docs/` until they agree (unless they already asked to document).
5. **Cite why** — each major number (RAM, GPU, cores) needs a one-line reason tied to the stack.
6. **Prefer existing docs** — extend README or `docs/` section rather than inventing a parallel format when one already exists.

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| "What hardware do I need?" / system requirements | Live CPU/RAM/GPU sampling (use [hardware-metrics](../hardware-metrics/SKILL.md)) |
| Documenting min/recommended specs in README or docs | Choosing which local LLM fits a PC (use [llmfit](../llmfit/SKILL.md)) |
| Sizing a laptop/desktop/VM for this repo | Cloud instance right-sizing from production metrics alone |
| Dev machine vs server/runtime requirements | Application code profiling (use compiled/interpreted-performance) |
| User asks to add hardware requirements to docs | Pure software API design with no runtime target |

When unsure and the user mentions machine specs, system requirements, or documenting hardware, **apply this skill**.

## Workflow Checklist

Copy and track:

```
Hardware requirements:
- [ ] Phase 0: Recon — stack, workload, existing requirement docs
- [ ] Phase 1: Classify workload and contexts (dev / run / server)
- [ ] Phase 2: Draft min + recommended specs with rationale
- [ ] Phase 3: Present suggestion to the user
- [ ] Phase 4: Ask whether to add to documentation
- [ ] Phase 5: If yes — write docs and link from README
```

## Phase 0 — Recon

Scan the project before proposing numbers:

| Signal | Look for |
|--------|----------|
| Language / runtime | `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `*.csproj` |
| Heavy deps | ML (`torch`, `tensorflow`), browsers (`playwright`), DBs, video, games, compilers |
| Containers | `Dockerfile`, `compose.yaml` — resource limits, base image, services |
| Infra | `.github/workflows`, cloud-init, Terraform — runner / VM size hints |
| Existing docs | README "Requirements", `docs/getting-started.md`, `SYSTEM_REQUIREMENTS.md` |
| Stated targets | README claims ("runs on Raspberry Pi", "needs CUDA 12", "16 GB recommended") |

Also note OS assumptions (Linux-only scripts, Windows paths, macOS-only tooling).

```bash
# Quick recon helpers (adapt to the repo)
ls -la README.md docs 2>/dev/null
rg -n -i "require|ram|gpu|cuda|memory|minimum|hardware|system requirements" README.md docs 2>/dev/null | head -40
```

## Phase 1 — Classify Workload

Pick the primary workload class (combine if multi-service):

| Class | Typical drivers | Spec focus |
|-------|-----------------|------------|
| **Docs / static site** | Markdown, SSG | Modest CPU/RAM; little disk |
| **Web app (API + UI)** | Node/Python/Go + optional DB | 2–4 cores, 4–8 GB; SSD for DB |
| **Data / ETL** | Large files, Spark, bulk I/O | RAM + disk throughput |
| **ML training / inference** | PyTorch, CUDA, large models | GPU VRAM, system RAM, CUDA stack |
| **Native / compiled** | C/C++, Rust, large link steps | CPU cores for parallel builds; RAM for link |
| **Browser automation** | Playwright/Puppeteer | Extra RAM per browser context |
| **Containers / compose** | Multi-service local stack | Sum of service mins + host overhead |
| **Embedded / edge** | Pi, Jetson, constrained images | Cap to target board; call out limits |

Define **contexts** you will size:

1. **Develop** — edit, build, test, lint, one local stack
2. **Run locally** — use the product without full contrib tooling (if different)
3. **Server / deploy** — production-like single node (if relevant; else say "see hosting docs")

## Phase 2 — Draft Specs

Produce **Minimum** and **Recommended** for each relevant context.

### Dimensions to cover

| Dimension | Include when |
|-----------|--------------|
| **OS** | Always (families + notes: Linux x86_64, macOS arm64, Windows WSL2, etc.) |
| **CPU** | Cores/threads; arch if relevant (x86_64, arm64) |
| **RAM** | GB; distinguish system RAM vs GPU VRAM |
| **Disk** | Free space + media (SSD strongly preferred when I/O-heavy) |
| **GPU** | Optional vs required; VRAM; CUDA/ROCm/Metal notes |
| **Network** | Only if downloads, sync, or multiplayer matter |
| **Display** | Only for GUI / game / design tools |

### Sizing heuristics (starting points — adjust with evidence)

Use these as **baselines**, then raise or lower with repo signals:

| Workload | Minimum (dev) | Recommended (dev) |
|----------|---------------|-------------------|
| Light web / CLI | 2 cores, 4 GB RAM, 10 GB free | 4 cores, 8 GB, SSD 20+ GB free |
| Full-stack + local DB | 2 cores, 8 GB, SSD 20 GB | 4+ cores, 16 GB, SSD 40+ GB |
| Playwright / heavy browsers | 4 cores, 8 GB | 4+ cores, 16 GB |
| Native large project | 4 cores, 8 GB | 8+ cores, 16–32 GB |
| Small ML / CPU inference | 4 cores, 16 GB | 8 cores, 32 GB |
| GPU ML (training / large models) | CUDA GPU 8 GB VRAM, 16 GB RAM | 16+ GB VRAM, 32+ GB RAM |

Always add **host overhead** (~1–2 GB RAM) when sizing compose stacks. Prefer citing Dockerfile `mem_limit`, CI `runs-on`, or model size over the table alone.

### Output shape (user-facing suggestion)

```markdown
# Hardware requirements — <project>

## Summary
<1–2 sentences: who this is for and the heaviest constraint>

## Development

| | Minimum | Recommended |
|--|---------|-------------|
| OS | | |
| CPU | | |
| RAM | | |
| Disk | | |
| GPU | | |

### Why these numbers
- **RAM**: <evidence>
- **CPU / GPU**: <evidence>
- **Disk**: <evidence>

## Local run (if different)
...

## Notes / optional
- GPU optional for X; required for Y
- Known weak machines: ...
```

Mark uncertainty explicitly ("estimated from PyTorch + 7B model weights; not load-tested").

## Phase 3 — Present to the User

Show the full suggestion **before** editing any files. Keep it scannable: table + short rationale. Offer to refine if the user names a target (e.g. "must run on 8 GB laptop").

## Phase 4 — Ask About Documentation

**Always ask** (unless the user already requested a docs write):

> Want me to add these hardware requirements to the project docs?

If **no** — stop after the suggestion; leave files unchanged.

If **yes** — proceed to Phase 5. Confirm path if ambiguous (README section vs `docs/hardware.md`).

## Phase 5 — Write Documentation

Follow [document-project](../document-project/SKILL.md) layout:

1. Prefer a dedicated doc under `docs/` when the project already uses `docs/` (e.g. `docs/hardware.md` or a section in `docs/getting-started.md`).
2. Keep README short: a **Hardware** / **System requirements** blurb + link to the full doc.
3. If there is no `docs/` tree and requirements are brief (one table), a README section is enough.
4. Do not duplicate long tables in both places — link instead.
5. Preserve any accurate existing requirements; replace only stale or conflicting text after noting the change.

### README blurb template

```markdown
## System requirements

See [Hardware requirements](docs/hardware.md) for minimum and recommended
CPU, RAM, disk, and GPU for development and local runs.
```

### `docs/hardware.md` skeleton

Use the Phase 2 output shape. Add a short "Last updated" or "Derived from" line when helpful (stack version, date). Tie setup steps to [getting-started](../document-project/SKILL.md) docs with relative links.

### Completion checklist

```
Docs write-back:
- [ ] User explicitly agreed to add requirements to documentation
- [ ] Full specs live in docs/ (or README if intentionally short)
- [ ] README links to full specs (if docs/ used)
- [ ] Min vs recommended both present with rationale
- [ ] No contradiction with Dockerfile/CI-stated limits (or contradictions explained)
```

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Editing README before asking | Present specs, then ask |
| One vague "8 GB recommended" line | Min + recommended table with why |
| Ignoring CUDA/GPU when torch/CUDA is required | Call out VRAM and CUDA as required or optional |
| Copying cloud VM SKUs as laptop specs | Translate to cores/RAM/disk humans understand |
| Measuring current machine and calling it "requirements" | Requirements are for target users; measure with hardware-metrics separately |
| Duplicating the full table in README and docs | Full table once; README links |

## Additional Resources

- Doc layout and README discipline: [document-project](../document-project/SKILL.md)
- Live host measurement: [hardware-metrics](../hardware-metrics/SKILL.md)
- Local LLM hardware fit: [llmfit](../llmfit/SKILL.md)
- Example outputs: [examples.md](examples.md)
