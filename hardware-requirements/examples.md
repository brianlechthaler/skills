# Hardware Requirements — Examples

## Example 1 — Full-stack web app (Node + Postgres)

**Signals:** `package.json`, `compose.yaml` with `postgres:16`, Playwright e2e optional.

**Suggestion (excerpt):**

### Development

| | Minimum | Recommended |
|--|---------|-------------|
| OS | Linux x86_64, macOS arm64, or Windows 11 + WSL2 | Same |
| CPU | 2 cores | 4+ cores |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB free SSD | 40 GB+ free SSD |
| GPU | Not required | Not required |

**Why:** Compose runs API + Postgres (~2–3 GB) plus Node/browser tooling; Playwright needs headroom when enabled.

**Ask:** "Want me to add these hardware requirements to the project docs?"

**Docs (after yes):** `docs/hardware.md` + README link under System requirements.

---

## Example 2 — PyTorch training project

**Signals:** `torch` with CUDA wheels in `requirements.txt`, README mentions fine-tuning 7B models.

**Suggestion (excerpt):**

### Development / local training

| | Minimum | Recommended |
|--|---------|-------------|
| OS | Linux x86_64 with NVIDIA driver | Ubuntu 22.04/24.04 LTS |
| CPU | 4 cores | 8+ cores |
| RAM | 16 GB | 32 GB |
| Disk | 50 GB free SSD (models + datasets) | 100 GB+ NVMe |
| GPU | NVIDIA, **8 GB VRAM**, CUDA 12.x | **16+ GB VRAM** |

**Why:** 7B LoRA fine-tunes typically need ~8–12 GB VRAM depending on batch/seq; datasets and checkpoints dominate disk.

**Ask before writing docs.** Mark CPU-only as unsupported if the training scripts require CUDA.

---

## Example 3 — User declines documentation

Agent presents the table and asks to add to docs. User says no.

**Correct behavior:** Leave README/`docs/` unchanged. Suggestion remains in the chat only.

---

## Example 4 — Existing README section

**Signals:** README already has `## Requirements` listing Node 20+ only (no hardware).

**After user agrees:** Extend that section with a hardware table *or* move detail to `docs/hardware.md` and keep Node version in README with a link to hardware. Do not create a second competing "System requirements" heading.
